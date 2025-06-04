def omit_none(**kwargs):
    return {k:v for k,v in kwargs.items() if v is not None}
