import pymongo
from pymongo.server_api import ServerApi
import pickle as pkl
from bson.binary import Binary
import sunpy.map
import matplotlib.pyplot as plt
from astropy.io import fits


def generate_img(harp_num,date,hour,minute,color_option='Grey'):
    client = pymongo.MongoClient("mongodb+srv://Annie:GSUADS123@cluster0.3e4grb6.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
    mydb = client["SolarImage"]
    collection = mydb.fits

    filename = 'hmi.sharp_cea_720s.'+str(harp_num)+'.'+str(date)+'_'+str(hour)+str(minute)+'00_TAI.magnetogram.fits'
    cursor = collection.find({'FILENAME': filename})
    if len(list(cursor))==1:
        for obj in list(collection.find({'FILENAME': filename})):
            hdul = fits.HDUList()
    
            primary_header = {}
            img_header = {}
            count=0
            for key, value in obj.items():
                if key.startswith('P_'):
                    primary_header[key.split('P_')[1]] = value
                else:
                    if key!='_id' and key!='DATA' and key!='FILENAME':
                        img_header[key] = value
                        count+=1
    
                if key=='DATA':
                    img_data = pkl.loads(value)
    
            compIMG_hdu = fits.CompImageHDU(data=img_data,header=fits.Header(img_header))

            hdul.append(compIMG_hdu)
            hdul.verify('fix')
            hdul.writeto('./temp.fits', overwrite=True)

            fig = plt.figure(figsize=(8,6))
            hmi_magmap = sunpy.map.Map('./temp.fits')
            
            if color_option=='Grey':
                hmi_magmap.plot()
            elif color_option=='Color':
                hmi_magmap.plot_settings['cmap'] = 'hmimag'
                hmi_magmap.plot_settings['norm'] = plt.Normalize(-1500, 1500)
                im_hmi = hmi_magmap.plot()
                cb = plt.colorbar(im_hmi, fraction=0.019, pad=0.1)
                cb.set_label("LOS Magnetic Field [Gauss]")
    
            plt.xlabel('Carrington Longitude [deg]',fontsize = 16)
            plt.ylabel('Latitude [deg]',fontsize = 16)
            plt.savefig('./static/images/banner/01.png', bbox_inches='tight')
            plt.switch_backend('Agg')
            #plt.show()
            #plt.close(fig)
            
            return 1
    else:
        return 0