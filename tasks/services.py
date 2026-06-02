def create_task(form, creator):
    task = form.save(commit=False)
    task.creator = creator
    task.save()
    return task


def delete_task(task):
    task.delete()
