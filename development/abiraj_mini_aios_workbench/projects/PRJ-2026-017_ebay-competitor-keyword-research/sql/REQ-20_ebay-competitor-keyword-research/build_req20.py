import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
OUT=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_ebay_competitor_keyword_SOLD.xlsx"
wb=openpyxl.Workbook(); ws=wb.active; ws.title="Competitor & Keyword"
cols=["Product Name","Competitor ID","Brand","Title","Sold Quantity","Price","Feedback Rate","Shipping type","Promotion Type & %","Primary Keywords","Secondary Keywords","Long-Tail Keywords","Notes"]
ws.append(cols)
hf=Font(bold=True,color="FFFFFF"); fill=PatternFill("solid",fgColor="2F5496")
for c in ws[1]: c.font=hf; c.fill=fill; c.alignment=Alignment(wrap_text=True,vertical="top")

KW={
 "Metal Shade Pendant Light":("Metal Shade Pendant Light, Metal Pendant Light, Hanging Pendant Light","Ceiling Pendant Shade, Industrial Pendant Light, Easy Fit Pendant Shade, Kitchen Pendant Light","Black Metal Shade Pendant Light for Kitchen Island, Industrial Easy Fit Metal Pendant Shade E27, Modern Chrome Metal Pendant Ceiling Light"),
 "Wall Light":("Wall Light, Wall Lamp, Wall Sconce","Indoor Wall Light, Bedside Wall Lamp, Industrial Wall Sconce, LED Wall Light","Black Industrial Wall Light for Living Room, Vintage Wall Sconce with Switch, Modern LED Bedside Wall Reading Lamp"),
 "Metal shade Ceiling Light":("Metal Ceiling Light, Ceiling Shade, Metal Pendant Shade","Industrial Ceiling Light, Metal Lampshade, Ceiling Light Fitting, Retro Ceiling Shade","Black Metal Ceiling Light Shade for Kitchen, Industrial Metal Pendant Shade E27, Vintage Metal Ceiling Lampshade Easy Fit"),
 "Glass shade ceiling light":("Glass Ceiling Light, Glass Pendant Light, Glass Shade","Clear Glass Pendant, Glass Lampshade, Ceiling Glass Light Fitting, Modern Glass Pendant","Clear Glass Globe Pendant Light for Kitchen Island, Vintage Glass Ceiling Shade E27, Modern Frosted Glass Hanging Light"),
 "Spider Light":("Spider Light, Spider Pendant, Multi-Head Pendant Light","Sputnik Light, Multi Light Pendant, Industrial Spider Lamp, Adjustable Spider Ceiling Light","Black Multi-Head Spider Pendant Light for Living Room, Industrial Sputnik Ceiling Light 6 Head, Adjustable DIY Spider Chandelier E27"),
 "Cage pendant light":("Cage Pendant Light, Cage Light, Metal Cage Pendant","Industrial Cage Light, Wire Cage Pendant, Vintage Cage Lamp, Cage Ceiling Light","Black Metal Cage Pendant Light for Kitchen, Industrial Wire Cage Hanging Lamp E27, Vintage Cage Ceiling Light Fitting"),
 "Pipe Light":("Pipe Light, Pipe Pendant Light, Steampunk Light","Industrial Pipe Light, Steampunk Pendant, Pipe Wall Light, Water Pipe Lamp","Industrial Steampunk Pipe Pendant Light for Kitchen Island, Black Metal Pipe Ceiling Light E27, Vintage Water Pipe Wall Lamp"),
 "Bulbs":("LED Bulb, Filament Bulb, Light Bulb","Edison Bulb, Vintage LED Bulb, E27 Bulb, Dimmable LED Filament Bulb","E27 Vintage Edison LED Filament Bulb Warm White, Dimmable Squirrel Cage Light Bulb, ST64 Amber Decorative LED Bulb 4W"),
 "Lamp Holder":("Lamp Holder, Bulb Holder, E27 Holder","Ceiling Rose Lamp Holder, Pendant Lamp Holder, Bakelite Bulb Holder, E27 Fitting","E27 Vintage Bakelite Pendant Lamp Holder with Cord Grip, Ceiling Rose Bulb Holder Kit, Screw E27 Fitting with Switch"),
}
SKU={"Metal Shade Pendant Light":"CRSF100BM+PHSH1PBRYB+SCRN70BM+LSFT220BM"}

# UK-ONLY dataset (all competitors verified "Located in ... United Kingdom", 2026-07-30)
DATA={
"Metal Shade Pendant Light":[
 ("372336415252","value-lights","ValueLights","Lampshade Ceiling Pendant Light Shade Easy Fit Metal","6,442+","GBP 17.99","99.8% (685K)","With postage","Save up to 10% Multi-buy"),
 ("113986270784","eshhopinguk","Country Club","Gem Wrap Twist Design Glamour Silver Metal Lamp Shade Easy Fit","317","GBP 118.95","99.5% (136.8K)","With postage","-"),
 ("333667118358","firstchoicelightingoutlet","firstchoicelighting","Set of 2 Modern Black Metal Swirl Easy Fit Ceiling Light Shade","268","GBP 23.45","99.7% (89.9K)","With postage","-"),
 ("405002496188","online336","Homion","Ancient Moroccan Style Metal Ceiling Light Shade Easy Fit Pendant","61+","GBP 99.99","99.8% (26.8K)","With postage","Save up to 6% Multi-buy"),
 ("202880784935","buybox786","Optimal Products","Silver Gem Wrap Twist Design Pendant Glamour Metal Lamp Shade","38","GBP 118.95","99.7% (220.4K)","With postage","-"),
],
"Wall Light":[
 ("115699570601","eat_sleep_buy_repeat","(not listed)","Vintage Industrial Wall Light Antique Retro Cage Bulkhead Gold Brass","257","GBP 64.99","100% (1.4K)","With postage","-"),
 ("353351065595","value-lights","ValueLights","Industrial Style Wall Light Polished Chrome with Glass Shades","180+","GBP 26.99 to 29.99","99.8% (685K)","With postage","From GBP 18.89 with coupon"),
 ("234566652967","burgesshandg","(not listed)","Vintage Industrial Wall Light Antique Retro Style Lamp Sconce","71","GBP 31.99","99.7% (9.8K)","With postage","-"),
 ("256403363785","sj_modern_antiques","Davey & Co","Davey & Co Style Industrial Bulkhead Wall Light Vintage Antique","57","GBP 57.99","98.5% (15.2K)","With postage","-"),
 ("364433876601","discountcdrom","(not listed)","Outdoor Vintage Replica Industrial Round Caged IP44 Bulkhead Wall Light","56","GBP 12.99","99.6% (410.1K)","With postage","-"),
],
"Metal shade Ceiling Light":[
 ("372257187156","value-lights","ValueLights","Ceiling Light Fitting 3 Way Chrome Spotlight Swirl","8,367","GBP 19.99","99.8% (685K)","With postage","-"),
 ("333667118358","firstchoicelightingoutlet","firstchoicelighting","Set of 2 Modern Black Metal Swirl Easy Fit Ceiling Light Shade","268","GBP 23.45","99.7% (89.9K)","With postage","-"),
 ("405002496188","online336","Homion","Ancient Moroccan Style Metal Ceiling Light Shade Easy Fit Pendant","61+","GBP 99.99","99.8% (26.8K)","With postage","Save up to 6% Multi-buy"),
 ("154043319055","homeessenceltd","Innoteck","Metal Drum Vintage Light Shade Modern Decorative Ceiling Pendant","58+","GBP 14.99","99.9% (60.1K)","With postage","-"),
 ("163799621837","goodwood-originals123","Unbranded","Lampshade Industrial Pendant Ceiling Light Silver Metal Retro Nordic","19+","GBP 14.00 to 29.00","100% (3.1K)","With postage","-"),
],
"Glass shade ceiling light":[
 ("372257187156","value-lights","ValueLights","Ceiling Light Fitting 3 Way Chrome Spotlight Swirl Glass","8,367","GBP 19.99","99.8% (685K)","With postage","-"),
 ("283064879219","picknmix.online","Giggi","Modern Chandelier Style Ceiling Pendant Light Shade K9","600","GBP 21.99","99.6% (21.9K)","With postage","-"),
 ("141200077246","buyitbetter_uk","ElekTek","ElekTek 3-Hook Ceiling Rose Pendant Plate Suspended Glass","516+","GBP 17.25 to 19.99","99.9% (55.5K)","With postage","Save up to 7% Multi-buy"),
 ("272110237788","moonlight_retail_15","MoonLight Retail","New Modern Vintage Industrial Retro Loft Glass Ceiling Lamp Shade","269+","GBP 32.47 to 35.83","100% (3.9K)","With postage","Save up to 5% Multi-buy"),
 ("333667118358","firstchoicelightingoutlet","firstchoicelighting","Set of 2 Modern Black Metal Swirl Easy Fit Ceiling Light Shade","268","GBP 23.45","99.7% (89.9K)","With postage","-"),
],
"Spider Light":[
 ("372474939568","loopsdirect","ThatCable","Multi Light Ceiling Pendant 6 Bulb Gloss Copper Industrial Adjustable","","GBP 94.99","98.3% (235.1K)","With postage","-"),
 ("303227195662","nationallighting","National Lighting","Adjustable Pendant Light Fitting Ceiling Rose E27 Industrial Spider","","GBP 13.42 to 59.92","99.6% (18.4K)","With postage","-"),
 ("317136278633","themiddleaisleuk23","(not listed)","6 Light Spider Pendant Ceiling Light Hemp Rope Industrial Multiple Hanging","","GBP 68.98","99.3% (4.7K)","With postage","Save up to 15% Multi-buy"),
 ("406427712394","ulsltd","Unbranded","Duplex Spider Fitting for Pendant Lamp Shades BC B22 Bayonet Cap","28","GBP 7.85","100% (1.6K)","With postage","-"),
 ("166809932104","mossodor_lighting","Mossodor","Black Pendant Light Industrial Ceiling Light Spider Modern Cluster E27","","GBP 32.95","98.3% (886)","With postage","Save up to 20% Multi-buy"),
],
"Cage pendant light":[
 ("372257190104","value-lights","ValueLights","Ceiling Light Shade Geometric Pendant Lampshade Industrial","429+","GBP 12.99 to 15.99","99.8% (685K)","With postage","Save up to 10% Multi-buy"),
 ("232708905363","value-lights","ValueLights","Industrial Metal Ceiling Pendant Light Shade Easy Fit","289+","GBP 22.99 to 25.99","99.8% (685K)","With postage","From GBP 20.69 with coupon"),
 ("131173303482","thelampfactoryuk","Unbranded","Black Wire Cage Light Shade Steel E27 Industrial Pendant","252","GBP 13.00","99.8% (22.6K)","With postage","-"),
 ("141264804458","thelampfactoryuk","Unbranded","Bronze Wire Cage Light Shade Steel E27 Industrial Pendant","157","GBP 13.00","99.8% (22.6K)","With postage","-"),
 ("372864053966","value-lights","ValueLights","Geometric Globe Lampshade Metal Pendant Ceiling Light Shade","125+","GBP 14.99 to 17.99","99.8% (685K)","With postage","10% off"),
],
"Pipe Light":[
 ("262744851290","sj_modern_antiques","(not listed)","Silver Industrial Ceiling Light Vintage Antique Pendant Pipe Cage","114","GBP 46.99","98.5% (15.2K)","With postage","-"),
 ("236319831602","industrial_cafe","Moonlight Retail","Industrial Vintage Ceiling Lights Metal Pipe Retro Loft Pendant Steampunk","","GBP 36.95 to 53.75","100% (1.1K)","With postage","-"),
 ("236319380461","industrial_cafe","Moonlight Retail","Industrial Steampunk Lighting Iron Pipe Edison Bulb Ceiling Bar Light Rope","","GBP 67.19 to 77.27","100% (1.1K)","With postage","-"),
 ("336171618850","industrial_cafe","Moonlight Retail","Industrial Steampunk Chandelier Iron Pipe Edison Bulb Ceiling Bar Light","","GBP 167.99 to 250.87","100% (1.1K)","With postage","-"),
 ("336163640353","industrial_cafe","Moonlight Retail","Industrial Steampunk Light Iron Pipe Edison Bulb Ceiling Chain 7 Heads","","GBP 101.91","100% (1.1K)","With postage","-"),
],
"Bulbs":[
 ("303695648760","auctionzltd","Kanlux","2x Vintage Filament LED Edison Screw Bulb E27 Decorative ST64","237","GBP 16.95","99.7% (84.9K)","With postage","Save up to 20% Multi-buy"),
 ("223224109836","safield-online","Auraglow","Auraglow Mysa LED Light Bulb Vintage Retro Edison Style E27 T30","180","GBP 10.99","99.8% (188.5K)","With postage","-"),
 ("142340181955","thelampfactoryuk","Unbranded","Vintage Edison Filament LED Bulb Teardrop E27 ES 4W Warm White","169","GBP 3.50","99.8% (22.6K)","With postage","-"),
 ("193185894331","safield-online","Auraglow","Auraglow Mysa LED Light Bulb Vintage Retro Edison Style G125 Globe","156+","GBP 16.99","99.8% (188.5K)","With postage","-"),
 ("353206988280","auctionzltd","Kanlux","E27 LED Vintage Edison Spiral Filament Industrial Bulb Amber","128","GBP 7.95","99.7% (84.9K)","With postage","Save up to 12% Multi-buy"),
],
"Lamp Holder":[
 ("155034392297","theyinltd","Unbranded","E27 Ceiling Rose Light Fitting Vintage Industrial Pendant Holder","88+","GBP 8.99","99.7% (5.5K)","With postage","-"),
 ("396977702027","gmuk.ltd","Luxa","Black Retro E27 Vintage Screw In Light Bulb Lamp Holder Ceiling Rose","38","GBP 8.99","100% (2.5K)","With postage","Save up to 5% Multi-buy"),
 ("363478927381","dqpltd","Unbranded","1x Brass Rose Ceiling Pendant Light Kit 1 Metre Flex ES E27","30","GBP 4.99","99.6% (185.3K)","With postage","Save up to 8% Multi-buy"),
 ("322867838398","ediscount247","Unbranded","CERTIFIED ES E27 Ceiling Rose Chain Pendant Lamp Holder Kit UK","28+","GBP 99.00","100% (12.6K)","With postage","-"),
 ("283939294098","bandhstore","Crown Lighting","E27 Chrome Ceiling Rose Pendant With Tube And Lamp Holder Fitting","27","GBP 29.95","100% (8.5K)","With postage","-"),
],
}

order=["Metal Shade Pendant Light","Wall Light","Metal shade Ceiling Light","Glass shade ceiling light","Spider Light","Cage pendant light","Pipe Light","Bulbs","Lamp Holder"]
total=0; sold_ok=0
for cat in order:
    pk,sk,lt=KW[cat]; rows=DATA[cat]
    for i,r in enumerate(rows):
        cid,seller,brand,title,sold,price,fb,ship,promo=r
        total+=1
        if sold.strip(): sold_ok+=1
        ws.append([cat if i==0 else "", cid, brand, title, sold, price, fb, ship, promo,
                   pk if i==0 else "", sk if i==0 else "", lt if i==0 else "", "Competitor seller: "+seller+"."])

widths=[22,15,20,42,11,17,15,14,22,30,34,46,30]
import openpyxl.utils as u
for i,w in enumerate(widths,1): ws.column_dimensions[u.get_column_letter(i)].width=w
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment=Alignment(wrap_text=True,vertical="top")
ws.freeze_panes="A2"
try:
    wb.save(OUT)
    print("rebuilt: %d rows, %d with sold history, %d blank" % (total, sold_ok, total-sold_ok))
except PermissionError:
    print("xlsx locked (open in Excel) - skipped save; data still available for import")
