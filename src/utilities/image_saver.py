import os
import traceback

def save_graph_image(graph, filename, silent=True):
    """
    Saves the generated image of the graph structure in the same directory as the script.
    
    :param graph: The graph object that supports the `get_graph().draw_mermaid_png()` method.
    :param filename: The name of the current script, used as the image file name.
    """
    try:
        # Construct the image path based on the given filename
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "graph_images",
            f"{os.path.splitext(filename)[0]}.png"
        )

        # Save the generated image of the graph structure
        with open(image_path, "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
        if (silent == False):
            print(f"Image saved as {image_path}")
    except Exception as e:
        print("An error occurred while saving the image:", e)
        traceback.print_exc()
