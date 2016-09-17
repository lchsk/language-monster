import inspect

def assert_subclasses(classes, class_, predicate):
    """Ensure that all classes are of required class_.

        classes([(string name, class)]): A list of tuples (name, class)

        class_(class): Required class

        predicate(function): Function to select items from classes based
            on the name. Must return either True of False.
    """

    for name, cbv in classes:
        if inspect.isclass(cbv) and predicate(name):
            assert issubclass(cbv, class_)
