def assign_labs(grouped_schedule, labs):
 for key, courses in grouped_schedule.items():
     #print(f"Time Slot and Days: {key}")
     #print("| {:<15} | {:<10} | {:<20} | {:<18} | {:<30} |".format("Course Code", "Lab Number", "Instructor", "Enrolled Students", "Status"))
     print("-" * 96)  # Separator line
     for course_code, details in courses.items():
         allocated_lab = None
         # max_lab_capcity = lab.capcity
         for lab in labs:
             if details['TimeSlot'] in lab.schedule and details['Days'] in lab.days_available:
                 continue  # Lab already occupied at this time and day
             if len(lab.schedule) < lab.capacity:
                 if details['Days'] not in lab.days_available:
                     lab.days_available.append(details['Days'])  # Update lab's available days
                 allocated_lab = lab
                 break
         if allocated_lab:
             allocated_lab.schedule.append(details['TimeSlot'])
             status = f"Assigned to Lab {allocated_lab.lab_number}"
         else:
             status = "Unable to assign due to capacity"
         print("| {:<15} | {:<10} | {:<20} | {:<18} | {:<30} |".format(course_code, allocated_lab.lab_number if allocated_lab else '-', details['Instructor'], details['EnrolledStudents'], status))

     for lab in labs:
      lab.days_available = []