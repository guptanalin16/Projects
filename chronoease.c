#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_TASKS 100
#define TASK_NAME_LEN 100

typedef struct Task {
    int day;
    int month;
    int year;
    char task[TASK_NAME_LEN];
} Task;

// Function to check if a year is a leap year or not
int isLeapYear(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

// Function to get the number of days in a month
int daysInMonth(int month, int year) {
    if (month == 2) {
        return isLeapYear(year) ? 29 : 28;
    }
    if (month == 4 || month == 6 || month == 9 || month == 11) {
        return 30;
    }
    return 31;
}

// Function to calculate the day of the week for a given date
// Returns 0 = Sunday, 1 = Monday, ..., 6 = Saturday
int getDayOfWeek(int day, int month, int year) {
    if (month < 3) {
        month += 12;
        year -= 1;
    }
    int k = year % 100;
    int j = year / 100;
    int weekday = (day + 13 * (month + 1) / 5 + k + k / 4 + j / 4 - 2 * j) % 7;
    return (weekday + 6) % 7; 
}

// Function to display the calendar for the entire month
void displayMonthCalendar(int month, int year) {
    const char *months[] = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    };
    const char *weekdays = "Sun Mon Tue Wed Thu Fri Sat";

    int days = daysInMonth(month, year);
    int firstDay = getDayOfWeek(1, month, year);

    printf("\n  %s %d\n", months[month - 1], year);
    printf("%s\n", weekdays);

    
    for (int i = 0; i < firstDay; i++) {
        printf("    ");
    }

    // Print all days of the month
    for (int day = 1; day <= days; day++) {
        printf("%3d ", day);
        if ((day + firstDay) % 7 == 0) {
            printf("\n");
        }
    }
    printf("\n");
}

Task tasks[MAX_TASKS];
int taskCount = 0;

// Function to load tasks from the file into the tasks array
void loadTasksFromFile() {
    FILE *file = fopen("tasks.txt", "r");
    if (file == NULL) {
        printf("No existing tasks file found. Starting fresh.\n");
        taskCount = 0;  
        return;
    }

    taskCount = 0;
    while (fscanf(file, "%d %d %d %[^\n]", &tasks[taskCount].day, &tasks[taskCount].month, &tasks[taskCount].year, tasks[taskCount].task) == 4) {
        taskCount++; 
    }
    fclose(file);
}

// Function to show all tasks
void showtasks() {
    loadTasksFromFile();  // Ensure tasks are loaded before showing

    if (taskCount == 0) {
        printf("No tasks available.\n");
        return;
    }

    printf("Tasks:\n");
    for (int i = 0; i < taskCount; i++) {
        printf("%d. %s (Due: %02d/%02d/%04d)\n", i + 1, tasks[i].task, tasks[i].day, tasks[i].month, tasks[i].year);
    }
}  

// Function to save all tasks back to the file
void saveTasksToFile() {
    FILE *file = fopen("tasks.txt", "w");
    if (file == NULL) {
        printf("Error opening file for writing!\n");
        return;
    }

    for (int i = 0; i < taskCount; i++) {
        fprintf(file, "%02d %02d %04d %s\n", tasks[i].day, tasks[i].month, tasks[i].year, tasks[i].task);
    }

    fclose(file);
}

// Function to add a task
void addTask() {
    if (taskCount >= MAX_TASKS) {
        printf("Task list is full! Cannot add more tasks.\n");
        return;
    }

    // Get the current date
    time_t t = time(NULL);
    struct tm *currentDate = localtime(&t);
    int currentDay = currentDate->tm_mday;
    int currentMonth = currentDate->tm_mon + 1;  // weekdays are 0-based
    int currentYear = currentDate->tm_year + 1900; // years are since 1900

    printf("Enter the task (max %d characters): ", TASK_NAME_LEN - 1);
    getchar(); // Clear buffer
    fgets(tasks[taskCount].task, TASK_NAME_LEN, stdin);
    

    printf("Enter the due date (DD MM YYYY): ");
    scanf("%d %d %d", &tasks[taskCount].day, &tasks[taskCount].month, &tasks[taskCount].year);

    // Compare the entered date with the current date
    if (tasks[taskCount].year < currentYear ||
        (tasks[taskCount].year == currentYear && tasks[taskCount].month < currentMonth) ||
        (tasks[taskCount].year == currentYear && tasks[taskCount].month == currentMonth && tasks[taskCount].day < currentDay)) {
        printf("Error: Cannot add a task for a past date.\n");
        return;
    }

    // If the date is valid, add the task to the file
    FILE *file = fopen("tasks.txt", "a");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }

    fprintf(file, "%02d %02d %04d: %s\n", tasks[taskCount].day, tasks[taskCount].month, tasks[taskCount].year, tasks[taskCount].task);
    fclose(file);

    taskCount++;
    saveTasksToFile();  //saves tasks after adding
    printf("Task added successfully!\n");
}

// Function to display tasks according to user's wish
void displayTasks() {
    loadTasksFromFile();
    if (taskCount == 0) {
        printf("No tasks available.\n");
        return;
    }
    int choice;
    printf("Do you want to display tasks for a particular date or all tasks?\n");
    printf("1. Tasks on particular date\n");
    printf("2. All tasks\n");
    printf("Enter your choice: ");
    scanf("%d", &choice);

    printf("Tasks:\n");
    if(choice == 1) {
        int day, month, year;
        printf("Enter the date (DD MM YYYY): ");
        scanf("%d %d %d", &day, &month, &year);

        printf("Tasks for %02d/%02d/%04d:\n", day, month, year);
        int found = 0;
        for (int i = 0; i < taskCount; i++) {
            if (tasks[i].day == day && tasks[i].month == month && tasks[i].year == year) {
                printf("%d. %s\n", i + 1, tasks[i].task);
                found = 1;
            }
        }
        if (!found) {
            printf("No tasks found for the specified date.\n");
        }
    } else if(choice == 2) {
        showtasks();
    } else {
        printf("Invalid choice\n");
    }
}

// Function to modify a task
void modifyTask() {
    loadTasksFromFile();
    showtasks();
    int index;
    printf("Enter the task number to modify (1-%d): ", taskCount);
    scanf("%d", &index);

    if (index < 1 || index > taskCount) {
        printf("Invalid task number!\n");
        return;
    }

    // Get the current date
    time_t t = time(NULL);
    struct tm *currentDate = localtime(&t);
    int currentDay = currentDate->tm_mday;
    int currentMonth = currentDate->tm_mon + 1;  // weekdays are 0-based
    int currentYear = currentDate->tm_year + 1900; // years are since 1900

    index--; // Convert to zero-based index
    printf("Enter the new task (max %d characters): ", TASK_NAME_LEN - 1);
    getchar(); // Clear buffer
    fgets(tasks[index].task, TASK_NAME_LEN, stdin);
    tasks[index].task[strcspn(tasks[index].task, "\n")] = '\0'; // Remove newline character

    printf("Enter the new due date (DD MM YYYY): ");
    scanf("%d %d %d", &tasks[index].day, &tasks[index].month, &tasks[index].year);

    // Compare the entered date with the current date
    if (tasks[index].year < currentYear ||
        (tasks[index].year == currentYear && tasks[index].month < currentMonth) ||
        (tasks[index].year == currentYear && tasks[index].month == currentMonth && tasks[index].day < currentDay)) {
        printf("Error: Cannot add a task for a past date.\n");
        return;
    }

    saveTasksToFile();
    printf("Task modified successfully!\n");
}

// Function to delete a task
void deleteTask() {
    loadTasksFromFile();  

    if (taskCount == 0) {
        printf("No tasks available.\n");
        return;
    }

    showtasks();  

    int index;
    printf("Enter the task number to delete (1-%d): ", taskCount);
    scanf("%d", &index);

    if (index < 1 || index > taskCount) {
        printf("Invalid task number!\n");
        return;
    }

    index--;  
    for (int i = index; i < taskCount - 1; i++) {
        tasks[i] = tasks[i + 1];  
    }

    taskCount--;  // Decrease the task count

    // Save the updated task list back to the file
    saveTasksToFile();

    printf("Task deleted successfully!\n");
}

// Function to show the menu in main
void menu() {
    printf("\n--- Calendar Task Manager ---\n");
    printf("1. Display Calendar\n");
    printf("2. Add Task\n");
    printf("3. Modify Task\n");
    printf("4. Delete Task\n");
    printf("5. Display Tasks\n");
    printf("6. Exit\n");
}

// Main function
int main() {
    int choice;

    while (1) {
        menu();
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                { 
                    int day, month, year;
                    printf("Enter a date (DD MM YYYY): ");
                    scanf("%d %d %d", &day, &month, &year);

                    // Validate the input
                    if (month < 1 || month > 12 || day < 1 || day > daysInMonth(month, year)) {
                        printf("Invalid date! Please enter a valid date.\n");
                        return 1;
                    }
                    displayMonthCalendar(month, year);
                    break;
                }
            case 2:
                addTask();
                break;
            case 3:
                modifyTask();
                break;
            case 4:
                deleteTask();
                break;
            case 5:
                displayTasks();
                break;
            case 6:
                printf("Exiting program. Goodbye!\n");
                return 0;
            default:
                printf("Invalid choice! Please try again.\n");
        }
    }

