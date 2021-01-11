# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 17:40:47 2020

@author: User
"""

import camelot
# import matplotlib.pyplot as plt
import time

def bl_scrape(file,start_time,doc_type):
    
    tables = camelot.read_pdf(file,
                              pages="1", 
                              flavor="stream",                          
                              table_areas=[
                                    "26, 784, 340, 709",        # Shipper/Exporter
                                    "26, 712, 340, 645",        # Consignee
                                    "340, 783, 461, 762",       # Booking No
                                    "461, 783, 581, 762",       # Bill of Lading No
                                    "26, 646, 340, 577",        # Notify Party
                                    "183, 577, 340, 556",       # Place of receipt
                                    "183, 553, 340, 529",       # Port of Loading
                                    "183, 529, 340, 506",       # Place of delivery
                                    "26, 576, 183, 556",        # Pre-Carriage By
                                    "28, 556, 183, 529",        # Ocean Vessel
                                    "28, 529, 183, 506",        # Port of Discharge
                                    "340, 556, 581, 529",       # Final Destination
                                    "340, 529, 581, 506",       # Type of movement
                                    "28, 296, 220, 278",        # Freight & Charges payable
                                    "220, 296, 298, 278",       # Service Contract No.
                                    "298, 296, 352, 278",       # Doc Form No.
                                    "350, 296, 411, 278",       # Commodity Code
                                    "410, 296, 487, 278",       # Exchange Rate
                                    "487, 243, 580, 221",       # Date Cargo Received
                                    "487, 221, 580, 200",       # Date laden on Board
                                    "487, 200, 580, 178",       # Place of Bill Issue
                                    "487, 178, 580, 157",       # Dated
                                    ],
                              )
    # tables
    #%%
    retJSON={}
    for table in tables:
        # table.to_csv('test_row10.csv',mode='a')
        # print({table.df[0][0]:" ".join(table.df[0][1:])})
        retJSON.update({table.df[0][0]:" ".join(table.df[0][1:])})
    # for x,y in c.items():
    #     print(x + ':    ' + y + '\n')
    #%%
    # camelot.plot(tables[0], kind='grid')
    # plt.show()
    
    # camelot.plot(tables[-1], kind='textedge')
    # plt.show()
    #%%
    tables2 = camelot.read_pdf(file,
                              pages="1", 
                              flavor="lattice",
                              table_areas=[
                                  "28, 497, 582, 319",      # Description of Goods
                                  ]
                              )
    tables2
    # camelot.plot(tables2[3], kind='joint')
    # plt.show()
    
   
    for i in range(0,tables2[0].df.shape[1]):
        # print({tables2[0].df[i][1]:tables2[0].df[i][2]})
        retJSON.update({tables2[0].df[i][1]:tables2[0].df[i][2]})   

    #%% 
    tables3 = camelot.read_pdf(file,
                              pages="2", 
                              flavor="stream",
                              table_areas=[
                                  "28, 754, 580, 130",      # Additional Information
                                  "364, 111, 566, 27",     # Signed by
                                  ],
                              )
    tables3
    # camelot.plot(tables3[-1], kind='contour')
    # plt.show()
    
    retJSON.update({"Additional Information":" ".join(tables3[0].df[0][1:])})
    retJSON.update({"Signed by":" ".join(tables3[-1].df[0][:])})
    
    #%%    
    stop_time=time.time() -start_time
    print(f"It takes {round(stop_time,2)} seconds to complete")
    retJSON.update({f"Time Taken":str(stop_time)})
    retJSON.update({"document_type":doc_type})
    
    # for x,y in c.items():
    #     print(x + ':    ' + y + '\n')
    return retJSON