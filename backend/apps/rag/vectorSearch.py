import marqo as mq
import pprint
import os, json
from utils.misc import get_last_user_message, add_or_update_system_message

from config import AppConfig
config = AppConfig()

class VectorSearch:
    def __init__(self):
        self.mq = mq.Client(url="http://localhost:8882")

    def index_search(self, index, q, limit=3, offset=0, filter_string=None, searchableAttributes=["*"],
                    showHighlights=True, searchMethod="TENSOR", attributesToRetrieve=None,
                    efSearch=2000, approximate=True, scoreModifiers=None):
        """
        Searches the specified index using the marqo client for documents matching the query (q).

        Args:
            q                     (str):     The search query.
            limit                 (int):     The maximum number of documents to return. Defaults to 10.
            offset                (int):     The starting document offset. Defaults to 20.
            filter_string         (str):     A filter string to refine results. Defaults to 0.
            searchableAttributes  (str):     Comma-separated list of searchable attributes. Defaults to None.
            showHighlights        (bool):    Whether to return highlighted snippets. Defaults to True.
            searchMethod          (str):     The search method ("TENSOR", etc.). Defaults to "TENSOR".
            attributesToRetrieve  (str):     Array of strings of attributes to retrieve. Defaults to None.
            efSearch              (int):     The number of elements to explore during indexing. Defaults to 2000.
            approximate           (bool):    Whether to use approximate search for faster results. Defaults to True.
            scoreModifiers        (dict):    Modifiers to influence document scores. Defaults to None.

        Returns a json format of the search output from mq.index(index).search().
        """

        output = self.mq.index(index).search(
        q=q,
        limit=limit,
        )

        return output 

    def output_parser(self, r_input, r=0.85, limit=3, integer=1):
        output_list = []

        for i in range(min(limit, len(r_input['hits']))):
            doc = r_input['hits'][i]
            doc_id = doc.get('_id')
            highlights = doc.get('_highlights', {})
            path = doc.get('path')  # Extract path
            score = doc.get('_score')  # Extract score

            if score < r:
                say = "The score is less than the threshold"
                continue

            # Ensure highlights is a dictionary, even if initially set to [{}]
            if isinstance(highlights, list) and len(highlights) > 0:
                highlights = highlights[0]  # Assuming only the first item matters

            content_keys = [key for key in doc.keys() if key.startswith('content_')]
            content_keys.sort(key=lambda x: int(x.split('_')[1]))
            content = {f'content_{str(j).zfill(2)}': doc[key] for j, key in enumerate(content_keys)}

            if integer == 1:
                # Mode 1: Filter content based on highlights
                content_filtered = {}
                highlight_numbers = [int(key.split('_')[1]) for key in highlights.keys() if key.startswith('content_')]
                for n in highlight_numbers:
                    # Attempt to add content_N, content_{N-1}, and content_{N+1} to content_filtered
                    for offset in (-1, 0, 1):
                        content_key = f'content_{str(n + offset).zfill(2)}'
                        if content_key in content:
                            content_filtered[content_key] = content[content_key]

                # Ensure content_filtered contains only up to 3 contents
                content_filtered_keys = list(content_filtered.keys())[:3]
                content_filtered = {key: content_filtered[key] for key in content_filtered_keys}

                doc_dict = {
                    '_id': doc_id,
                    '_highlights': highlights,
                    'content': [content_filtered],
                    'path': path,  # Include path
                    '_score': score  # Include score
            }

            elif integer == 2:
                # Mode 2: Use all content fields without filtering
                doc_dict = {
                    '_id': doc_id,
                    '_highlights': highlights,
                    'content': [content],
                    'path': path,  # Include path
                    '_score': score  # Include score
            }

            output_list.append(doc_dict)

        if not output_list:
            return False

        output_string = pprint.pformat(output_list, indent=2)

        with open('./testing/output_dic.json', 'w') as f:
            json.dump(output_list, f, indent=2)

        with open('./testing/output.txt', 'w') as f:
            f.write(output_string)
        with open('./testing/debug_output.txt', 'w') as debug_file:
            json.dump(r_input, debug_file, indent=2)


        pMs = r_input.get("processingTimeMs", 0)
        print(f"Rag processing time: {pMs} ms")
        return output_string
        
V = VectorSearch()


# q = "yepyepyepyep"
# index = "masterdocs"
# limit = 3
# r = 0.85
# r_output = V.index_search(index, q, limit)
# output_string = V.output_parser(r_output, r, integer = 1)
# print(output_string)





def rag_template(template: str, context: str, query: str):
    template = template.replace("[context]", context)
    template = template.replace("[query]", query)
    return template

def rag_addition(
    messages,
    template,
    r, # relevance threshold
    hybrid_search,
):
    print(f"Rag input: {messages} {template} {hybrid_search}")

    query = get_last_user_message(messages)

    integ = config.RAG_STATE
    if query != "":
        r_output = V.index_search(query, limit=3)
        f_output = V.output_parser(r_output, r=r, integer=integ, limit=3)
        if f_output is False:
            # TODO: Handle this case
            print("Relevance threshold check failed.")
        else:
            try:
                parsed_output = json.loads(f_output)
            except json.JSONDecodeError:
                print("Failed to parse JSON response from output_parser.")
        

    context_string = ""
    citations = []
    for item in parsed_output:
        content_N = []
        # Check if 'content' key exists and is a list with at least one item
        if item.get("content") and isinstance(item["content"], list) and len(item["content"]) > 0:
            # Iterate over each key in the first item of the 'content' list
            for key, value in item["content"][0].items():
                # Check if the key starts with 'content_'
                if key.startswith("content_"):
                    content_N.append(value)
        if content_N:
            context_string += "\n\n".join(
                [text for text in content_N if text is not None]
                )
        citations.append({
            "source": item.get("_id", ""),
            "document": content_N,
            "metadata": {
                "path": item.get("path", ""),
                "score": item.get("_score", 0),
                "highlights": item.get("_highlights", {})
            }
        }
        )

    context_string = context_string.strip()
    return context_string, citations
