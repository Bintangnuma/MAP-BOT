import sqlite3
import matplotlib

matplotlib.use('Agg')  # Menginstal backend Matplotlib untuk menyimpan file dalam memori tanpa menampilkan jendela
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Mengimpor modul yang akan memungkinkan kita bekerja dengan proyeksi peta

class DB_Map():
    def __init__(self, database):
        self.database = database  # Menginisiasi jalur database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Menghubungkan ke database
        with conn:
            # Membuat tabel, jika tidak ada, untuk menyimpan kota pengguna
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Menyimpan perubahan

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mencari kota dalam database berdasarkan nama
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Menambahkan kota ke daftar kota pengguna
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Menunjukkan bahwa operasi berhasil
            else:
                return 0  # Menunjukkan bahwa kota tidak ditemukan

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Memilih semua kota pengguna
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Mengembalikan daftar kota pengguna

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Mendapatkan koordinat kota berdasarkan nama
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Mengembalikan koordinat kota

    def create_graph(self, path, cities):
        # Membuat konteks grafis baru dengan proyeksi PlateCarree.
        # PlateCarree adalah proyeksi geografis sederhana di mana longitud dan latitud
        # ditampilkan sebagai garis vertikal dan horizontal, masing-masing.
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Menambahkan gambar bumi default ke peta.
        # Gambar latar belakang ini disediakan oleh library Cartopy dan mencakup
        # visualisasi permukaan bumi, lautan, dan relief utama.
        ax.stock_img()

        # Iterasi melalui daftar kota untuk menampilkan mereka di peta.
        for city in cities:
            # Mendapatkan koordinat kota. Fungsi ini harus mengembalikan tuple dengan latitud dan longitud kota.
            coordinates = self.get_coordinates(city)

            # Memeriksa apakah koordinat kota berhasil diambil.
            if coordinates:
                # Membuka tuple koordinat ke variabel lat (latitud) dan lng (longitud).
                lat, lng = coordinates

                # Menampilkan marker di peta di posisi yang didefinisikan oleh koordinat kota.
                # 'color='r'' menetapkan warna marker menjadi merah, 'linewidth=1' menetapkan ketebalan garis marker,
                # 'marker='.'' menentukan bentuk marker (titik).
                plt.plot([lng], [lat], color='r', linewidth=1, marker='.', transform=ccrs.Geodetic())

                # Menambahkan teks (nama kota) di dekat marker.
                # '+3' dan '+12' ke longitud dan latitud menghasilkan teks relatif terhadap marker
                # sehingga teks tidak tumpang tindih dengan marker dan tetap dapat dibaca.
                plt.text(lng + 3, lat + 12, city, horizontalalignment='left', transform=ccrs.Geodetic())

        # Menyimpan gambar yang dibuat ke file di jalur yang ditentukan dalam argumen 'path'.
        plt.savefig(path)

        # Menutup konteks matplotlib untuk membebaskan sumber daya.
        plt.close()

    def draw_distance(self, city1, city2):
        # Menampilkan garis antara dua kota untuk menampilkan jarak
        city1_coords = self.get_coordinates(city1)
        city2_coords = self.get_coordinates(city2)
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.stock_img()
        plt.plot([city1_coords[1], city2_coords[1]], [city1_coords[0], city2_coords[0]], color='red', linewidth=2,
                 marker='o', transform=ccrs.Geodetic())
        plt.text(city1_coords[1] + 3, city1_coords[0] + 12, city1, horizontalalignment='left',
                 transform=ccrs.Geodetic())
        plt.text(city2_coords[1] + 3, city2_coords[0] + 12, city2, horizontalalignment='left',
                 transform=ccrs.Geodetic())
        plt.savefig('distance_map.png')
        plt.close()


if __name__ == "__main__":
    m = DB_Map("database.db")  # Membuat objek yang akan berinteraksi dengan database
    m.create_user_table()   # Membuat tabel dengan kota pengguna, jika tidak sudah ada