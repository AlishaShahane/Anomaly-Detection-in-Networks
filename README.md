# Anomaly Detection in Networks
### Required folder structure:
        /root
          /datasets
            /enron_by_day
            /autonomous
            /voices
            /p2p_Gnutella
          /outputs (empty folder)
          anomaly.py

### Command to run
      The code takes input dataset as an argument. Run the following command in the root folder:
	    python anomaly.py datasets/<folder_name>
      Eg: python anomaly.py datasets/enron_by_day/

### Output
    A text file and plot for every dataset will be written in the /outputs folder.

### Required Packages:
    Networkx: $ pip install networkx
