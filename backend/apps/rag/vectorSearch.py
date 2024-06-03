import marqo
import pprint
import streamlit as st
import os, json

mq = marqo.Client(url="http://localhost:8882")


def index_search(index, q, limit=5, offset=0, filter_string=None, searchableAttributes=["*"],
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

    output = mq.index(index).search(
      q=q,
      limit=limit,
    )

    output_string = ''
    # output_string += f'Limit: {limit}\n'
    # output_string += f'Offset: {offset}\n'
    # output_string += f'Processing Time Ms: {output["processingTimeMs"]}\n'
    # output_string += f'Query: {q}\n\n'
    for i in range(min(limit, len(output['hits']))):
        output_string += pprint.pformat(output['hits'][i])
        output_string += '\n\n'

    with open('output.txt', 'w') as f:
        f.write(output_string)

    metadata =  {
        'Limit': limit,
        'Offset': offset,
        'Processing Time Ms': output["processingTimeMs"],
        'Query': q
    }

    # for hit in output['hits']:
    #     yield hit

    return output_string, metadata

# pprint.pprint(index_search(index, query))

def delete_index(index):
    try:
        mq.index(index).delete()
        st.success("Index successfully deleted.")
    except:
        st.error("Index does not exist.")
        pass

def reset_state():
    st.session_state['results'] = {}
    st.session_state['page'] = -1
   