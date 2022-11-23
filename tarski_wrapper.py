#! /usr/bin/env python

from xml import dom
import tarski
from tarski.theories import Theory
import tarski.fstrips as fs
from tarski.io import fstrips as iofs
from tarski.io import FstripsWriter
from tarski.syntax import land


class PlanningTask:
    def __init__(self, name, task_name):
        self.name = name
        self.lang = self.get_language()
        self.cost = self.lang.function("total-cost", self.lang.Real)

        # Problem instance
        self.problem = iofs.create_fstrips_problem(
                    domain_name=f'{name}-domain',
                    problem_name=f'{task_name}-problem',
                    language=self.lang,
                )

        self.problem.metric(self.cost(), fs.OptimizationType.MINIMIZE)
        self.problem.init = tarski.model.create(self.lang)
        self.problem.init.set(self.cost(), 0)
        self.type_by_name = {}
        self.object_by_name = {}

    def get_type(self, name):
        return self.type_by_name[name]

    def get_object(self, name):
        return self.object_by_name[name]

    def constant_cost(self, cost):
        return iofs.AdditiveActionCost(self.problem.language.constant(cost, self.problem.language.get_sort('Integer')))

    def get_language(self):
        return iofs.language(self.name, theories=[Theory.EQUALITY, Theory.ARITHMETIC])

    def add_object_type(self, name, *args):
        t = self.lang.sort(name, *args)
        self.type_by_name[name] = t
        return t

    def add_predicate(self, name, *args):
        return self.lang.predicate(name, *args)

    def get_argument(self, name, object_type):
        return self.lang.variable(name, object_type)

    def add_function(self, name, *args):
        # nargs = [a for a in args]
        # print(nargs)
        # nargs.append(self.lang.Real)
        # print(*nargs)
        return self.lang.function(name, *args, self.lang.Real, )

    def add_object(self, name, object_type):
        if isinstance(object_type, str) and object_type in self.type_by_name:
            object_type = self.type_by_name[object_type]
        o = self.lang.constant(name, object_type)
        self.object_by_name[name] = o
        return o

    def add_action(self, name, arguments, precondition, add_effects, delete_effects, action_cost):
        effects = [fs.DelEffect(f) for f in delete_effects]
        effects.extend([fs.AddEffect(f) for f in add_effects])
        if type(action_cost) == int or type(action_cost) == float:
            action_cost = self.constant_cost(action_cost)
        else:
            action_cost = iofs.AdditiveActionCost(action_cost)
        return self.problem.action(name=name, parameters=arguments, 
                                    precondition=precondition, 
                                    effects=effects, cost=action_cost)

    def add_init_fact(self, predicate):
        self.problem.init.add(predicate)

    def set_init_value(self, function, value):
        self.problem.init.set(function, value)

    def add_goal_facts(self, predicates):
        self.problem.goal = land(*predicates, flat=True)

    def write_PDDL_files(self, domain_file, problem_file):
        writer = FstripsWriter(self.problem)
        with open(domain_file, 'w', encoding='utf8') as file:
            file.write(writer.print_domain().replace(":numeric-fluents",""))
        with open(problem_file, 'w', encoding='utf8') as file:
            file.write(writer.print_instance())


    def domain_to_PDDL(self):
        writer = FstripsWriter(self.problem)
        return writer.print_domain().replace(":numeric-fluents","")

    def problem_to_PDDL(self):
        writer = FstripsWriter(self.problem)
        return writer.print_instance()
