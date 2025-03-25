import requests
import os

def download_image(url, save_path):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {save_path}")
    else:
        print(f"❌ Failed to download {url} (Status: {response.status_code})")

def scrape_gallery(gallery_id):
    api_url = f"https://nhentai.net/api/gallery/{gallery_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Gagal mengambil galeri {gallery_id}! Status: {response.status_code}")
        return
    
    # Ambil JSON dari API
    gallery_json = response.json()
    
    # Ambil media_id
    media_id = gallery_json["media_id"]
    print(f"✅ media_id ditemukan: {media_id}")

    # Buat folder penyimpanan
    folder_path = f"nhentai_images/{gallery_id}"
    os.makedirs(folder_path, exist_ok=True)

    # Download Cover Image
    cover_url = f"https://i3.nhentai.net/galleries/{media_id}/1.jpg"
    download_image(cover_url, f"{folder_path}/cover.jpg")

    # Ambil jumlah halaman
    num_pages = gallery_json["num_pages"]
    print(f"📄 Total halaman: {num_pages}")

    # Download semua halaman
    for page in range(1, num_pages + 1):
        image_url = f"https://i2.nhentai.net/galleries/{media_id}/{page}.jpg"
        download_image(image_url, f"{folder_path}/{page}.jpg")

    print("✅ Semua gambar berhasil diunduh!")

if __name__ == "__main__":
    gallery_id = input("Masukkan ID gallery: ").strip()
    scrape_gallery(gallery_id)
