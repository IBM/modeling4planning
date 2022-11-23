#! /usr/bin/env python

from tarski_wrapper import PlanningTask
import os
import argparse
import random
from random_word import RandomWords


DEFAULT_NAMES = {
    "objects" : { "ball" : "ball", "room" : "room", "gripper" : "gripper"},
    "actions" : { "move" : "move", "pick" : "pick", "drop" : "drop"},
    "predicates" : {"ball" : "ball", "room" : "room", "gripper" : "gripper", "at-robby" : "at-robby", "at" : "at", "free" : "free", "carry" : "carry" }
}
names = DEFAULT_NAMES

# names = {
#     "objects" : { "ball" : "snack", "room" : "cell", "gripper" : "pocket"},
#     "actions" : { "move" : "crawl", "pick" : "hide", "drop" : "reveal"},
#     "predicates" : {"ball" : "snack", "room" : "cell", "gripper" : "pocket", "at-robby" : "agent-location", "at" : "location", "free" : "available", "carry" : "carry" }
# }


def main(args):
    random.seed(args.seed)
    def random_value(c):
        return random.choice(c)

    r = RandomWords()

    if args.randomize_names_objects:
        for k,v in names["objects"].items():
            names["objects"][k] = r.get_random_word()
        
    if args.randomize_names_predicates:
        for k,v in names["predicates"].items():
            names["predicates"][k] = r.get_random_word()

    if args.randomize_names_actions:
        for k,v in names["actions"].items():
            names["actions"][k] = r.get_random_word()


    def get_ball_name(i):
        return names["objects"]["ball"]+str(i)

    def get_room_name(i):
        return names["objects"]["room"]+str(i)

    def get_gripper_name(i):
        return names["objects"]["gripper"]+str(i)

    def get_init_room(args, rooms):
        return random_value(rooms) if args.randomize_location else rooms[0]

    def get_goal_room(args, rooms):
        return random_value(rooms) if args.randomize_location else rooms[1]

    def get_init_room_robby(args, rooms):
        return random_value(rooms) if args.randomize_location else rooms[0]


    domain_name = "gripper-generated"
    name = args.problem
    prob = PlanningTask(domain_name, name)

    # Predicates
    room = prob.add_predicate(names["predicates"]["room"], "object")
    ball = prob.add_predicate(names["predicates"]["ball"], "object")
    gripper = prob.add_predicate(names["predicates"]["gripper"], "object")
    atrobby = prob.add_predicate(names["predicates"]["at-robby"], "object")
    at = prob.add_predicate(names["predicates"]["at"], "object", "object")
    free = prob.add_predicate(names["predicates"]["free"], "object")
    carry = prob.add_predicate(names["predicates"]["carry"], "object", "object")

    # Actions 
    f = prob.get_argument("from", "object")
    t = prob.get_argument("to", "object")

    prob.add_action(names["actions"]["move"], arguments=[f, t], 
                        precondition=room(f) & room(t) & atrobby(f),
                        add_effects=[atrobby(t)],
                        delete_effects=[atrobby(f)],
                        action_cost=1)

    o = prob.get_argument("obj", "object")
    r = prob.get_argument("room", "object")
    g = prob.get_argument("gripper", "object")

    prob.add_action(names["actions"]["pick"], arguments=[o, r, g], 
                        precondition=ball(o) & room(r) & gripper(g) & at(o, r) & atrobby(r) & free(g),
                        add_effects=[carry(o, g)],
                        delete_effects=[at(o, r), free(g)],
                        action_cost=1)

    prob.add_action(names["actions"]["drop"], arguments=[o, r, g], 
                        precondition=ball(o) & room(r) & gripper(g) & carry(o, g) & atrobby(r),
                        add_effects=[at(o, r), free(g)],
                        delete_effects=[carry(o, g)],
                        action_cost=1)

    ## --------------------------- ##
    # Instance related part 
    os.makedirs(domain_name, exist_ok=True)
    goals = []
    # Objects, Initial state, Goal
    rooms = []
    for i in range(args.rooms):
        o = prob.add_object(get_room_name(i), "object")
        rooms.append(o)
        prob.add_init_fact(room(o))

    for i in range(args.balls):
        o = prob.add_object(get_ball_name(i), "object")
        prob.add_init_fact(ball(o))
        # Locations
        r = get_init_room(args, rooms)
        prob.add_init_fact(at(o,r))
        r = get_goal_room(args, rooms)
        goals.append(at(o,r))

    for i in range(args.grippers):
        o = prob.add_object(get_gripper_name(i), "object")
        prob.add_init_fact(gripper(o))
        prob.add_init_fact(free(o))

    prob.add_init_fact(atrobby(get_init_room_robby(args, rooms)))        

    # Goal
    prob.add_goal_facts(goals)

    prob.write_PDDL_files(os.path.join(domain_name,"domain.pddl"), os.path.join(domain_name, "%s.pddl" % name))
    # return prob.domain_to_PDDL(), prob.problem_to_PDDL()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--grippers", help="The number of grippers", type=int, default=2)
    parser.add_argument("--balls", help="The number of balls", type=int)
    parser.add_argument("--rooms", help="The number of rooms", type=int, default=2)

    parser.add_argument("--seed", help="The seed for random init and goal location", type=int, default=2022)
    parser.add_argument("--randomize-location", help="Randomize object locations", action='store_true')
    parser.add_argument("--randomize-names-objects", help="Randomize object names", action='store_true')
    parser.add_argument("--randomize-names-predicates", help="Randomize predicate names", action='store_true')
    parser.add_argument("--randomize-names-actions", help="Randomize action names", action='store_true')

    parser.add_argument("--problem", help="Problem name", default="problem")

    args = parser.parse_args()

    main(args)