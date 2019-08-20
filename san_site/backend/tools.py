def str2bool(v):
    if hasattr(v, 'lower'):
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return v in ("yes", "true", "t", "1")
