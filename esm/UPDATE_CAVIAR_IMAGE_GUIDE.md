# Quick Guide: Update Caviar Page Image

## Problem
The Caviar page is using a placeholder image URL that doesn't exist, so the image is broken.

## Solution: Find and Update the Real Image URL

### Step 1: Find the Caviar Image URL

**Option A: From WordPress Media Library**
1. Go to **Media → Library** in WordPress admin
2. Search for "Caviar" or scroll to find the Caviar artwork image
3. Click on the image
4. Copy the **File URL** (should be something like: `https://elliotspencermorgan.com/wp-content/uploads/2025/09/CaviarPainting.jpg`)

**Option B: From Homepage**
1. Go to https://elliotspencermorgan.com/
2. Right-click on the Caviar image
3. Select "Copy Image Address" or "Copy Image Link"
4. This gives you the correct URL

### Step 2: Update the Caviar Page

1. Go to **Pages → All Pages**
2. Find "Caviar" and click **Edit**
3. Click the **⋮** (three dots) in top-right
4. Select **Code editor**
5. Find and replace (Ctrl+F):
   - **Find:** `/wp-content/uploads/2024/12/caviar.jpg`
   - **Replace with:** `[paste the actual URL you found in Step 1]`
   - There should be **2 instances** to replace:
     - One in the `<script type="application/ld+json">` (schema)
     - One in the `<img src=` tag
6. Click **Update** to save

### Step 3: Verify

1. Visit https://elliotspencermorgan.com/caviar/
2. Refresh the page (Ctrl+F5)
3. The Caviar artwork image should now display correctly!

---

## Expected Image URL Format

The correct URL should look like one of these:
- `https://elliotspencermorgan.com/wp-content/uploads/2025/09/CaviarPainting.jpg`
- `https://elliotspencermorgan.com/wp-content/uploads/2025/09/caviar.jpg`
- `https://elliotspencermorgan.com/wp-content/uploads/YYYY/MM/filename.jpg`

**NOT** `lookoverhere.xyz` - that was an error from the browser detection.

---

## Alternative: Upload New Image

If you can't find the existing Caviar image:

1. Go to **Media → Add New**
2. Upload the Caviar artwork image
3. After upload, click the image and copy the **File URL**
4. Follow Step 2 above to update the page

---

## For Future Artwork Pages

When creating new artwork pages, always:
1. Upload the image to Media Library first
2. Copy the actual File URL from Media Library
3. Use that URL in the page template
4. This avoids placeholder/broken image issues

---

**Once updated, the Caviar page will be 100% complete with the real artwork image!**
