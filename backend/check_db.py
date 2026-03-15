from data.data import Session, Image, TaskImage, Task

with Session() as session:
    print("=" * 60)
    print("IMAGES TABLE:")
    print("=" * 60)
    images = session.query(Image).all()
    for img in images:
        print(f"ID: {img.id}, Path: {img.path}")
    
    print("\n" + "=" * 60)
    print("TASK_IMAGES TABLE:")
    print("=" * 60)
    task_images = session.query(TaskImage).all()
    for ti in task_images:
        print(f"ID: {ti.id}, Task ID: {ti.task_id}, Image ID: {ti.image_id}")
    
    print("\n" + "=" * 60)
    print("TASKS TABLE:")
    print("=" * 60)
    tasks = session.query(Task).all()
    for task in tasks:
        print(f"ID: {task.id}, Title: {task.title}, User ID: {task.user_id}")
