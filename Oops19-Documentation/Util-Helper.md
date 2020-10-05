# Oops19 High Heels Mod - Helper
The Helper tools manage sim lookup. It will be merged with the o19sim code.

When using the console it was a pain to specify an in-game sim. The helper reads all available sim names and adds them to a list.

Getting a sim is now straightforward:
```
o19.sim.sim 123         # Returns a sim with sim_id starting with 123
o19.sim.sim A#          # Return a sim with the 1st name starting, ending or containing an A
o19.sim.sim B#G         # Return a sim with a B in the 1st and a G in the last name. Could be 'Bella Goth'
```

The '#' sign separates the 1st and last name. For a sim with spaces in the name quote the whole parameter - if you ever want to write it out.

The helper class itself tries to provide an object with sim, sim_id, sim_info, sim_name, sim_filename while many values are never needed. The o19sim class fetches these paramters on demand.

sim_name is defined as 'First Name#Last Name'. As '#' is not allowed in the name it is a much better separator than '_' or ' ' and allows proper splitting.

sim_filename is the same as sim_name but with a few characters removed.

## More
It offers an expand_string() method to support custom lookups. Instead of entering 'EVERYDAY' one may enter 'e' or 'ev' and get 'EVERYDAY' back.

With write_to_console() long dicts can be printed (max 1024 chars for each output()) without dropping information.