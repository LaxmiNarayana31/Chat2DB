import traceback

def handle_exception(e):
    # Get the traceback as a string
    traceback_str = traceback.format_exc()
    print(traceback_str)

    # Get the line number of the exception
    line_no = traceback.extract_tb(e.__traceback__)[-1][1]
    print(f"Exception occurred on line {line_no}")
    return str(e)
