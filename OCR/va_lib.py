# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 09:28:07 2019

@author: Acceval Pte Ltd
"""

import matplotlib.pyplot as plt
import numpy as np
import time
# from mpl_toolkits.mplot3d import proj3d
# from mpl_toolkits.mplot3d import axes3d

def va(
        start_time, 
        buyer_request, 
        sup1_tier_weight, 
        sup2_tier_weight, 
        sup3_tier_weight, 
        sup1_tier_price,
        sup2_tier_price,
        sup3_tier_price,
        sup1_VA,
        sup2_VA,
        ):
    # buyer_request = 800
    
    #%% Supplier weight tiers
    # sup1_tier_weight = [0,250]
    # sup2_tier_weight = [0,280]
    # sup3_tier_weight = [0,300]
    
    #%% Supplier net Landing Pricing tiers
    # sup1_tier_price = [1260,1200]
    # sup2_tier_price = [1200,1180]
    # sup3_tier_price = [1200,1100]
    
    # sup1_VA = [ 0.2, 0.4]   # min max
    # sup2_VA = [ 0.2, 0.4]   # min max
    sup3_VA = [ 1-sup1_VA[1]-sup2_VA[1], 1-sup1_VA[0]-sup2_VA[0]]
    sup3_VA = [ round(x,2) for x in sup3_VA]
    
    #%%
    # fixed_sup2 = 0.2
    
    def total_price(buyer_request,fixed_sup2 = 0.2):
        
        # Set weight range for sup 2 to constant,
        # then change later using for loop
        w2_range = int(fixed_sup2*buyer_request)
        
        # Set weight range for sup 1
        w1_range = np.arange(buyer_request-w2_range+1)
        
        # Set weight range for supplier 3 = total - sup1 - sup2
        w3_range = buyer_request - w2_range - w1_range
        
        # Set price tiers for sup 1
        p1=np.zeros(shape=buyer_request-w2_range+1,dtype = 'int')
        p1[w1_range<sup1_tier_weight[1]+1] = sup1_tier_price[0]
        p1[w1_range>sup1_tier_weight[1]] = sup1_tier_price[1]
        
        # Set price for Sup 2
        # Because sup 2 only 1 value, so p2 also 1 value
        if fixed_sup2 * buyer_request < sup2_tier_weight[1]:
            p2 = sup2_tier_price[0]
        else:
            p2 = sup2_tier_price[1]
        
        p3=np.zeros(shape=buyer_request-w2_range+1,dtype = 'int')
        p3[w3_range<sup3_tier_weight[1]+1] = sup3_tier_price[0]
        p3[w3_range>sup3_tier_weight[1]] = sup3_tier_price[1]
            
        #total = np.sum([w1_range,w3_range,w2_range],axis=0)
            
        total_price = np.sum([p1*w1_range,p2*w2_range,p3*w3_range],axis=0)
        
    
        return total_price/1000, w1_range*100/buyer_request
    
    def plot_all(buyer_request, sup2_VA, n_pts=21):
        
        """""""""""""""
        Initialisation
        """""""""""""""
        pr = []
        minprice=[]
        maxprice=[]
        # fig = plt.figure()
        # fig.set_figwidth(12)
        # fig.set_figheight(6)
        # ax1 = fig.add_subplot(1, 2, 1)
        # ax1.set_facecolor('0.95')
        min_ind = int((1-sup2_VA[1])*buyer_request+1)  
        min_sup1 = int(sup1_VA[0]*buyer_request)
        max_sup1 = int(sup1_VA[1]*buyer_request+1)
        
        """""""""""""""""""""""""""""""""""""""""""""""
        Obtaining data for prices across supplier 2
        Taking 21 points from min to max supplier VA
        """""""""""""""""""""""""""""""""""""""""""""""
        a = np.linspace(sup2_VA[0],sup2_VA[1],n_pts).tolist()
        sup2_pts = [round(i,2) for i in a]  # [0.2, 0.21, 0.22, 0.23, 0.24,...]
        
        data = []
        
        for value in sup2_pts:
        # Running calc_bestprice function
            price, w1_range_norm = total_price(buyer_request,fixed_sup2 = value)
            minprice.append(price.min())
            maxprice.append(price.max())
            
            # The price matrix is a concatenation of variable-sized vector different
            # supplier 2 VA, therefore we take smallest sample sized based on
            # highest supplier 2 VA and used that size for other VA values.
            price_chopped = price[0:min_ind]
            pr.append(list(price_chopped))
            # ax1.plot(w1_range_norm,price)
            data.append(list(price))
            # print(len(price))
        
        """""""""""""""""""""""""""""""""""""""""""""""
        Finding Best price within the bounded region
        """""""""""""""""""""""""""""""""""""""""""""""
        # min list in list of prices
        res = [min(idx) for idx in zip(*pr)]
        
        # min price within for bounded region in supplier 1 - y
        min_price_y = min(res[min_sup1:max_sup1])   
        
        # Supplier 1 best price index
        sup1_bp_ind = max([i for i, j in enumerate(res) if j == min_price_y])  # Index obtianed from minimum
               
        if sup1_bp_ind>=max_sup1:
            sup1_bp_ind = max_sup1-1
        #bp_ind = res.index(min_price_y)
        
        # Location of minimum price y in x for suuplier 1
        min_price_x = sup1_bp_ind*100/buyer_request
        
        d=min(pr, key=lambda x: x[1])
        
        # Supplier 2 best price index 
        sup2_bp_ind=pr.index(d)
        # Plot best price as a red dot on figure
        # ax1.scatter(min_price_x, min_price_y,c='r')
                
        # Supplier 2 in percentage volume (list)
        sup2_legend = [int(x*100) for x in sup2_pts]
        
        # Supplier2 percentage volume where minimum price occurs
        min_va_sup2 = sup2_legend[sup2_bp_ind]
        
      #    ax1.annotate(f"The Optimum price is\nRM{min_price_y}k.\nat \
      # Supplier 1 VA = {int(min_price_x)}%,\n Supplier 2 VA = \
      # {min_va_sup2}%,\nand Supplier 3 VA =\
      # {100-int(min_price_x)-min_va_sup2}%",
      #    xy = (min_price_x, min_price_y), xytext = (-20, 40),
      #    textcoords = 'offset points', ha = 'right', va = 'bottom',
      #    bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
      #    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        
        """""""""""""""""""""""""""""""""
        Plotting vertical min_max VA for Supplier 1 
        """""""""""""""""""""""""""""""""
        # ax1.plot([sup1_VA[0]*100, sup1_VA[0]*100],[min(minprice), max(maxprice)],'r--')
        # ax1.text(sup1_VA[0]*100, max(maxprice), 'Sup 1\nmin VA\n', \
        #          horizontalalignment='center')
        # ax1.plot([sup1_VA[1]*100, sup1_VA[1]*100],[min(minprice), max(maxprice)],'r--')
        # ax1.text(sup1_VA[1]*100, max(maxprice), 'Sup 1\nmax VA\n', \
        #          horizontalalignment='center')
        # ax1.grid(None,'both','both')
        
        # # Legend
        # ax1.legend(sup2_legend,title = 'Percentage Volume(%)\nSupplier 2',fontsize='small',\
        #            bbox_to_anchor=(0.8, 0.5),loc='center left')
        # ax1.set_title("Price Distribution across VA for supplier 1\n\n",\
        #               fontweight="bold")
        # ax1.set_xlabel("Percentage Volume (%)\n(supplier 1)")
        # ax1.set_ylabel("Total Price (x RM 1k)")
        
        """""""""""""""""""""""
        3D Plot for 3 suppliers
        """""""""""""""""""""""
    #     ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        W, V = np.meshgrid(w1_range_norm, sup2_legend)
        PR = np.array(pr)   # Z-Data = price for 3D plot
        
    #     ax2.plot_surface(W, V, PR,rstride=1, cstride=1, cmap='bone')
    #     ax2.set_title("3D Price Distribution across VA \nfor supplier 1 and 2",\
    #                   fontweight="bold")
    #     ax2.set_xlabel('\nPercentage Volume (%)\n supplier 1')
    #     ax2.set_ylabel('\nPercentage Volume (%)\n supplier 2')
    #     ax2.set_zlabel('\nTotal Price (x RM 1k)')
    #     ax2.scatter(min_price_x,min_va_sup2, min_price_y,color='r')
      
    #     """""""""""""""""""""""""""""""""
    #     3D annotation of optimum price
    #     """""""""""""""""""""""""""""""""
    #     x2, y2, _ = proj3d.proj_transform(min_price_x,min_va_sup2, \
    #                                       min_price_y, ax2.get_proj())
    #     label = ax2.annotate(f"The Optimum price is\nRM{min_price_y}k.\nat \
    # Supplier 1 VA = {int(min_price_x)}%,\n Supplier 2 VA = \
    # {min_va_sup2}%,\nand Supplier 3 VA =\
    # {100-int(min_price_x)-min_va_sup2}%", xy = (x2, y2), xytext = (-30, 90),
    #     textcoords = 'offset points', ha = 'right', va = 'bottom',
    #     bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
    #     arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
      
    #     """
    #     Auto update 3D annotation.
    #     """
    #     def update_position(e):
    #         x2, y2, _ = proj3d.proj_transform(min_price_x,min_va_sup2, \
    #                                           min_price_y, ax2.get_proj())
    #         label.xy = x2,y2
    #         label.update_positions(fig.canvas.renderer)
    #         fig.canvas.draw()
    #     fig.canvas.mpl_connect('button_release_event', update_position)
      
    #     plt.show()   
        
    #     return pr,minprice,maxprice
    
    # pr,min1,max1 = plot_all(sup2_VA, n_pts=21)
                
        return pr, minprice, maxprice, min_price_x, min_price_y, min_va_sup2, w1_range_norm, data, W, V, PR
    
    pr, min1, max1, min_price_x, min_price_y, min_va_sup2, w1_range_norm, data, W, V, PR = plot_all(buyer_request, sup2_VA, n_pts=21)
    
    time_taken = time.time()-start_time
    # W = [list(x) for x in W]
    # V = [list(x) for x in V]
    # PR = [list(x) for x in PR]
    
    retJSON = { 
                "time_taken" : round(time_taken,5),
                'min_price_x': min_price_x,
                'min_price_y': min_price_y,
                'Sup1_weight': list(w1_range_norm),       
                'Price_ori': data,                      # For 2D plot
                'Price_chopped': pr,                    # For 3D Plot - need same length                         
                'Min VA Supplier 2': min_va_sup2,           
                'minprice': min1,
                'maxprice': max1,
                'x_3D': W.tolist(),
                'y_3D': V.tolist(),
                'z_3D': PR.tolist(),
                }
    
    return retJSON
#     