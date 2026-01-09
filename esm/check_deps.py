
try:
    from PIL import Image
    import requests
    import reportlab
    from sklearn.cluster import KMeans
    import numpy as np
    print("ALL IMPORTS OK: PIL, requests, reportlab, sklearn")
except ImportError as e:
    print(f"MISSING IMPORT: {e}")
