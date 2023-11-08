from typing import List


class App:
    """"""

    def __init__(self):
        """Constructor."""
        self.modules_to_run = []
        # initialization of other valiables

        # get module list
        self.modules_to_run = self.__load_configuration()

    def __load_configuration(self) -> List:
        """Get the configured module list."""
        # for example
        return ["Mod_A", "Mod_D", "Mod_F"]

    def __init_modules_to_run(self) -> List:
        """Returns a list of initialized objects of the configured classes."""
        # import classes from module package
        from modules import *

        # list of objects to run
        tmp = []

        for item_str in self.modules_to_run:
            # create object from class name string
            # and append it to tmp list
            class_object = # init module class
            if class_object:
                tmp.append(class_object)

        return tmp

    def run(self) -> None:
        """Main procedure."""
        # Thread objects
        th_to_run = self.__init_modules_to_run()

        for th in th_to_run:
            # run the module
            th.start()

        # continuation of the procedure
