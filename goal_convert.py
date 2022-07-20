
# Creates the contents and sorts the formatting
def goal_convert(content, goal_list):
    del content["submit"]
    del content["goals[]"]
    content['exercise_type'] = content["exercise_type"].lower()

    goal_string = ", ".join(goal_list)

    if goal_string[-2:] == ", ":
        goal_string = goal_string[:-2]

    content['goals'] = goal_string

    return content
