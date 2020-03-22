class Args(dict):
  def __init__(self, args_list, arg_spec):
    assert type(arg_spec) is list
    for i in range(len(arg_spec)):
      arg_str = args_list[i]
      spec = arg_spec[i]
      if type(spec) is str: # spec is the name of the argument
        self[spec] = arg_str
      else:
        assert type(spec) is tuple
        arg_name, arg_type = spec
        if '_' == arg_str: # underscore meand dont-care
          self[arg_name] = None
        elif type(arg_type) is list: # type is the range of its value
          assert arg_str in arg_type
          self[arg_name] = arg_str
        else:
          self[arg_name] = arg_type(arg_str)

  def __getattr__(self, name):
    return self[name]
