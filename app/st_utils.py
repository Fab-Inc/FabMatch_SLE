from io import StringIO
from contextlib import contextmanager
from threading import current_thread
import sys

import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import SCRIPT_RUN_CONTEXT_ATTR_NAME

@contextmanager
def st_redirect(src, dst, interfun=None):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                if interfun is not None:
                    output_func(interfun(buffer.getvalue()))
                else:
                    output_func(buffer.getvalue())
            else:
                old_write(b)
        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write

@contextmanager
def st_stdout(dst, interfun=None):
    with st_redirect(sys.stdout, dst, interfun):
        yield

@contextmanager
def st_stderr(dst, interfun=None):
    with st_redirect(sys.stderr, dst, interfun):
        yield

def parse_stdout(ntot):
    def parse_stdout_(stdout):
        sosplit = stdout.split("\n")
        if len(sosplit) > 1:
            last = sosplit[-2]
        else:
            last = 0
        return float(last) / ntot
    return parse_stdout_
