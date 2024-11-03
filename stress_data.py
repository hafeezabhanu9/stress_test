import os
import psutil
import time
import requests
import multiprocessing
import logging
import mysql.connector
from mysql.connector import Error

# Set up logging
logging.basicConfig(filename='stress_test.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

THRESHOLD = 80

# Stress increase functions
def increase_memory_stress():
    memory_list = []
    process = psutil.Process(os.getpid())
    while process.memory_percent() < THRESHOLD:
        memory_list.append(' ' * 1024 * 1024)  # 1 MB per iteration
        logging.info(f"Memory Usage: {process.memory_percent()}%")
    logging.info("Memory stress test reached target usage.")

def increase_disk_stress():
    with open("stress_test_file", "wb") as f:
        while psutil.disk_usage('/').percent < THRESHOLD:
            f.write(b'0' * 1024 * 1024 * 10)  # Write 10 MB at a time
            logging.info(f"Disk Usage: {psutil.disk_usage('/').percent}%")
    logging.info("Disk stress test reached target usage.")
    os.remove("stress_test_file")

def increase_network_stress():
    url = "https://www.google.com/"
    while (psutil.net_io_counters().bytes_recv * 100 / psutil.virtual_memory().total) < THRESHOLD:
        requests.get(url)
        logging.info(f"Network usage estimated: {(psutil.net_io_counters().bytes_recv * 100 / psutil.virtual_memory().total):.2f}%")
    logging.info("Network stress test reached target usage.")

def increase_cpu_stress():
    def stress():
        while True:
            pass  # Infinite loop to max out CPU

    processes = [multiprocessing.Process(target=stress) for _ in range(multiprocessing.cpu_count())]
    for p in processes:
        p.start()
        logging.info(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
    time.sleep(5)  # Run for a few seconds to increase CPU usage
    for p in processes:
        logging.info(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
        p.terminate()
    logging.info("CPU stress test completed.")

def increase_mysql_stress(host, user, password, database):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Connected to MySQL server for stress test.")
            cursor = connection.cursor()

            while True:
                cursor.execute("INSERT INTO student (id, name, grade) VALUES (4, 'Browny', 'A'), (25, 'Rock', 'B'), (13679, 'Jack', 'C'), (2568935, 'Clary', 'B') ON DUPLICATE KEY UPDATE name = VALUES(name), grade = VALUES(grade);")
                connection.commit()

                cursor.execute("SELECT COUNT(*), AVG(id), SUM(id) FROM student;")
                results = cursor.fetchall()
                logging.info(f"MySQL stress test query results: {results}")

                # Simulate deletion to maintain table size and intensify load
                cursor.execute("DELETE FROM student WHERE id > 5;")
                connection.commit()
        else:
            logging.error("Failed to establish connection to MySQL.")

    except mysql.connector.Error as err:
        logging.error(f"MySQL connection error: {err}")
        print(f"Error: {err}")  # Print error message for easier debugging
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"Error: {e}")  # Print error message for easier debugging
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.info("MySQL stress test connection closed.")

# Monitoring functions
def memory_stress_test():
    usage = psutil.virtual_memory().percent
    logging.info(f"Memory Usage: {usage}%")
    if usage < THRESHOLD:
        logging.info("Increasing memory stress to exceed threshold.")
        increase_memory_stress()
    else:
        logging.info("Memory usage exceeded threshold!")

def disk_stress_test():
    usage = psutil.disk_usage('/').percent
    logging.info(f"Disk Usage: {usage}%")
    if usage < THRESHOLD:
        logging.info("Increasing disk stress to exceed threshold.")
        increase_disk_stress()
    else:
        logging.info("Disk usage exceeded threshold!")

def network_stress_test():
    logging.info("Increasing network stress to attempt to reach threshold.")
    increase_network_stress()

def cpu_stress_test():
    usage = psutil.cpu_percent(interval=1)
    logging.info(f"Initial CPU Usage: {usage}%")
    if usage < THRESHOLD:
        logging.info("Increasing CPU stress to exceed threshold.")
        increase_cpu_stress()
    else:
        logging.info("CPU usage exceeded threshold!")

def mysql_stress_test():
    exporter_url = "http://192.168.29.232:9104/metrics"  # Updated to use the IP of vm_1
    thresholds = {
        "process_cpu_seconds_total": 1.0  # Set a threshold for CPU usage in seconds
    }

    try:
        response = requests.get(exporter_url)
        response.raise_for_status()

        metrics = {}
        for line in response.text.splitlines():
            if line.startswith("#"):
                continue
            if "process_cpu_seconds_total" in line:
                try:
                    metrics["process_cpu_seconds_total"] = float(line.split()[-1])
                except ValueError:
                    logging.warning(f"Could not convert value to float: {line}")

        # Check CPU time threshold
        if "process_cpu_seconds_total" in metrics:
            logging.info(f"process_cpu_seconds_total: {metrics['process_cpu_seconds_total']}")
            if metrics["process_cpu_seconds_total"] < thresholds["process_cpu_seconds_total"]:
                logging.info("MySQL process CPU usage is below threshold. Starting MySQL stress test.")

                # Call increase_mysql_stress with connection parameters
                increase_mysql_stress(
                    host="192.168.29.39",  # Updated to use the IP of vm_2
                    user="root",
                    password="Bhanu@123",  # Updated password
                    database="school"
                )
            else:
                logging.info("MySQL process CPU usage exceeded threshold. No additional stress applied.")
        else:
            logging.warning("process_cpu_seconds_total metric not found.")

    except requests.RequestException as e:
        logging.error(f"Failed to retrieve metrics from mysqld_exporter: {e}")

def main():
    while True:
        print("\nSelect an option:")
        print("1. Memory Stress Testing")
        print("2. Disk Stress Testing")
        print("3. Network Stress Testing")
        print("4. CPU Stress Testing")
        print("5. MySQL Stress Testing")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            memory_stress_test()
        elif choice == '2':
            disk_stress_test()
        elif choice == '3':
            network_stress_test()
        elif choice == '4':
            cpu_stress_test()
        elif choice == '5':
            mysql_stress_test()
        elif choice == '6':
            logging.info("Exiting")
            print("Exiting")
            break
        else:
            logging.warning("Invalid option selected.")
            print("Enter a valid option")

if __name__ == "__main__":
    main()
