import os
import sys
import traci
import csv  # 1. Import the built-in csv module

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def run():
    sumoBinary = "sumo-gui" 
    sumoCmd = [sumoBinary, "-c", "osm.sumocfg"]
    traci.start(sumoCmd)

    step = 0
    
    # 2. Open a new CSV file in write mode
    with open('vehicle_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # 3. Write the header row
        writer.writerow(['Step', 'Active_Vehicles', 'Vehicle_ID', 'Speed_kmh'])
        
        try:
            while step < 3600: 
                traci.simulationStep()
                
                vehicle_count = traci.vehicle.getIDCount()
                vehicle_ids = traci.vehicle.getIDList()
                
                # Print a clean summary to the terminal so it doesn't get flooded
                print(f"Step {step}: Logged {vehicle_count} vehicles to CSV")
                
                for veh_id in vehicle_ids:
                    speed_ms = traci.vehicle.getSpeed(veh_id)
                    speed_kmh = speed_ms * 3.6
                    
                    # 4. Write the current vehicle's data as a new row in the CSV
                    writer.writerow([step, vehicle_count, veh_id, round(speed_kmh, 2)])
                    
                step += 1
                
        except traci.exceptions.FatalTraCIError:
            print("\nSimulation window was closed by the user.")

    try:
        traci.close()
    except traci.exceptions.FatalTraCIError:
        pass

if __name__ == "__main__":
    run()