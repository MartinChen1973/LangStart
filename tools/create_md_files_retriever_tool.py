import sys
import os

from utilities.create_retriever_from_md_files import create_retriever_from_md_files, find_md_files
from utilities.create_retriever_from_urls import create_retriever_from_urls, load_urls

from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults

import os


def create_md_files_retriever_tool(app_data_folder):
    """Creates a retriever tool for markdown files in the org_information folder."""
    md_folder_path = os.path.join(app_data_folder, "docs", "org_information")
    md_files = find_md_files(md_folder_path)

    md_files_tool = create_retriever_tool(
        retriever=create_retriever_from_md_files(md_files),
        name="org_information",
        description="Retriever for information stored in markdown files.",
    )
    return md_files_tool
