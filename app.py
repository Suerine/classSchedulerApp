import streamlit as st
import pandas as pd
import constraint


st.set_page_config(page_title="Lab Scheduler", page_icon="" , layout="wide")

# ---- HEADER SECTION ----
with st.container():
 st.image('USIU_Africa_Logo.png')
 st.title('Lab Assignment App') 
 st.write("Input course details, lab capacities, instructor availability, and other relevant parameters. The app intelligently assigns courses to available lab slots based on specified time slots, days, instructor preferences, and lab capacities.")

# --- UPLOAD SECTION ----
with st.container():
 uploaded_file = st.file_uploader("Choose a file")
 if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)
 
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)


class Lab:
    def __init__(self, lab_number, capacity):
        self.lab_number = lab_number
        self.capacity = capacity
        self.schedule = []
        self.days_available = []

# Define a function to read and process the file
def process_schedule_file(file_path):
    schedule_data = {}
    with open(file_path) as f:
        for line in f:
            line_data = line.strip().split(',')
            time_slot = line_data[0]
            days = line_data[1]
            course_code = line_data[2]
            course_name = line_data[3]
            credits = int(line_data[4])
            instructor = line_data[5]
            enrolled_students = int(line_data[6])
            max_capacity = int(line_data[7])
            schedule_data[course_code] = {
                'TimeSlot': time_slot,
                'Days': days,
                'CourseName': course_name,
                'Instructor': instructor,
                'EnrolledStudents': enrolled_students,
                'MaxCapacity': max_capacity
            }
    return schedule_data

file_path = 'SofSUndergraduteCourseSchedule.txt'
schedule_data = process_schedule_file(file_path)

labs = [
 Lab(1, 60), Lab(2, 60), Lab(3, 60), Lab(4, 60), Lab(5, 60),
 Lab(6, 60), Lab(7, 60), Lab('GLab', 100), Lab('HLab', 100), Lab('SLab', 100),
]

#Grouping the courses according to time
def group_by_time(schedule_data):
 grouped_schedule = {}
 for course_code, entry in schedule_data.items():
     time_slot = entry["TimeSlot"]
     days = entry["Days"]
     key = f"{time_slot}/{days}"
     if key in grouped_schedule:
         grouped_schedule[key][course_code] = entry
     else:
         grouped_schedule[key] = {course_code: entry}
 return grouped_schedule

grouped_schedule = group_by_time(schedule_data)


def assign_labs(grouped_schedule, labs):
 problem = constraint.Problem()

 for course_code, _ in grouped_schedule.items():
   problem.addVariable(course_code, [lab.lab_number for lab in labs])

 # Add constraint to ensure each lab is assigned at most once
 problem.addConstraint(constraint.AllDifferentConstraint())

 solution = problem.getSolution()
 return solution

# assign_labs(grouped_schedule, labs)

# Streamlit App
st.header('Assigned Labs and Course Schedule')

time_slot = []
course_codes = []
lab_numbers = []
instructors = []
enrolled_students = []
statuses = []


for key, courses in grouped_schedule.items():
    print(f"Time Slot and Days: {key}")
    print("| {:<15} | {:<10} | {:<20} | {:<18} | {:<30} |".format("Course Code", "Lab Number", "Instructor", "Enrolled Students", "Status"))
    print("-" * 96)  # Separator line
    st.subheader(f'Time Slot and Days: {key}')
    lab_assignment_table = "| Course Code | Lab Number | Instructor | Enrolled Students | Status |\n"
    lab_assignment_table += "| --- | --- | --- | --- | --- |\n"
    for course_code, details in courses.items():
        allocated_lab = None
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
        lab_assignment_table += f"| {course_code} | {allocated_lab.lab_number if allocated_lab else '-'} | {details['Instructor']} | {details['EnrolledStudents']} | {status} |\n"
        print("| {:<15} | {:<10} | {:<20} | {:<18} | {:<30} |".format(course_code, allocated_lab.lab_number if allocated_lab else '-', details['Instructor'], details['EnrolledStudents'], status))
        time_slot.append(key)
        course_codes.append(course_code)
        lab_numbers.append(allocated_lab.lab_number if allocated_lab else '-')
        instructors.append(details['Instructor'])
        enrolled_students.append(details['EnrolledStudents'])
        statuses.append(status)

    for lab in labs:
     lab.days_available = []
    st.markdown(lab_assignment_table)

data = pd.DataFrame (
   {
    'Time Slot' : time_slot,
    'Course Code': course_codes,
    'Lab Number': lab_numbers,
    'Instructor': instructors,
    'Enrolled Students': enrolled_students,
    'Status': statuses
   }
)

st.write('##')
edited_schedule = st.data_editor(data, num_rows="dynamic")

st.header('Course Schedule')
st.write(schedule_data)
