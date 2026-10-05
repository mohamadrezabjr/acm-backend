def check_dependencies(person, dependencies):
    dependency_table = {
        'student_id' : person.student_id,
        'first_name' : person.first_name,
        'last_name' : person.last_name,
        'phone' : person.user.phone,
    }
    for dependency in dependencies:
        if not dependency_table[dependency]:
            return False
    return True