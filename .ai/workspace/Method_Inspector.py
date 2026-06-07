try:
    # Get the GUI object
    mdGUI = moneydance.getUI()
    
    # Get all attributes/methods
    methods = dir(mdGUI)
    
    # Filter for methods related to 'account' or 'show' or 'goto'
    relevant_methods = []
    for m in methods:
        ml = m.lower()
        if 'account' in ml or 'show' in ml or 'goto' in ml or 'view' in ml:
            relevant_methods.append(m)
            
    # Write to file
    out_path = r"C:\Working\Sandbox\moneydance\Jump To Account (Extension)\.ai\workspace\api_methods.txt"
    with open(out_path, "w") as f:
        f.write("Methods found on MoneydanceGUI:\n")
        f.write("="*40 + "\n")
        for m in sorted(relevant_methods):
            f.write(m + "\n")
            
    print "Successfully dumped API methods to: " + out_path
except Exception as e:
    print "Error introspecting API:", e
