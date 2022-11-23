# modeling4planning
Python code for easier generation of planning tasks by wrapping Tarski.
An example of using the wrapper can be seen through generators.

## Dependencies  
The only dependence at this point is on [Tarski](https://github.com/aig-upf/tarski), which can be installed via pip with 
```
pip install tarski
```

## Generators
### Gripper domain generator for variable number of balls/rooms/grippers. Optional randomization of all names.

```
./gripper_generator.py --randomize-names-objects --randomize-names-predicates --randomize-names-actions --randomize-location  --balls 8 --grippers 3 --rooms 4  
```

