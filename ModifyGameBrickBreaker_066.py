import tkinter as tk

# Base class untuk objek game
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    # Mendapatkan posisi objek dalam koordinat canvas
    def get_position(self):
        return self.canvas.coords(self.item)

    # Menggerakkan objek pada canvas
    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    # Menghapus objek dari canvas
    def delete(self):
        self.canvas.delete(self.item)

# Kelas untuk bola
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]  # Arah awal (kanan atas)
        self.speed = 5  # Kecepatan bola
        # Membuat bola di canvas
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    # Memperbarui posisi bola
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # Pantulan dinding kiri dan kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1

        # Pantulan dinding atas
        if coords[1] <= 0:
            self.direction[1] *= -1

        # Gerakkan bola sesuai arah dan kecepatan
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    # Deteksi dan tangani tabrakan dengan objek lain
    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5

        # Pantulan bola ke arah yang berlawanan
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        # Tabrakan dengan brick
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

# Kelas untuk paddle
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80  # Lebar paddle
        self.height = 10  # Tinggi paddle
        self.ball = None  # Bola yang berada di paddle (jika ada)
        # Membuat paddle di canvas
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    # Menyambungkan bola dengan paddle
    def set_ball(self, ball):
        self.ball = ball

    # Menggerakkan paddle dengan offset
    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Membatasi gerakan paddle agar tetap di dalam canvas
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:  # Gerakkan bola bersama paddle jika ada
                self.ball.move(offset, 0)

# Kelas untuk brick
class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}  # Warna berdasarkan jumlah hit

    def __init__(self, canvas, x, y, hits):
        self.width = 75  # Lebar brick
        self.height = 20  # Tinggi brick
        self.hits = hits  # Jumlah hit sebelum hancur
        color = Brick.COLORS[hits]  # Warna brick
        # Membuat brick di canvas
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    # Mengurangi hit saat terkena bola
    def hit(self):
        self.hits -= 1
        if self.hits == 0:  # Hancur jika hits habis
            self.delete()
        else:  # Perbarui warna sesuai jumlah hit
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

# Kelas utama untuk game
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3  # Nyawa awal
        self.score = 0  # Skor awal
        self.level = 1  # Level awal
        self.width = 610  # Lebar canvas
        self.height = 400  # Tinggi canvas
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}  # Menyimpan objek game
        self.ball = None  # Bola dalam game
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()  # Membuat brick di awal game

        self.hud = None
        self.setup_game()
        # Binding tombol panah untuk menggerakkan paddle
        self.canvas.focus_set()
        self.canvas.bind('<KeyPress-Left>',
                         lambda event: self.paddle.move(-15))
        self.canvas.bind('<KeyPress-Right>',
                         lambda event: self.paddle.move(15))

    # Persiapan awal game
    def setup_game(self):
        self.add_ball()  # Tambahkan bola ke game
        self.update_hud()  # Perbarui HUD
        self.text = self.draw_text(300, 200, 'Press Space to start')
        # Binding tombol spasi untuk memulai game
        self.canvas.bind('<space>', lambda _: self.start_game())

    # Tambahkan bola ke game
    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    # Membuat brick di level
    def create_bricks(self):
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

    # Menambahkan satu brick
    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    # Menampilkan teks di canvas
    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    # Memperbarui tampilan HUD (Lives, Score, Level)
    def update_hud(self):
        text = f'Lives: {self.lives}  Score: {self.score}  Level: {self.level}'
        if self.hud is None:
            self.hud = self.draw_text(100, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    # Mulai permainan
    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    # Loop utama game
    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:  # Semua brick hancur
            self.level += 1
            self.ball.speed += 1
            self.create_bricks()
            self.setup_game()
        elif self.ball.get_position()[3] >= self.height:  # Bola jatuh
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:  # Game over
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:  # Setup ulang jika masih ada nyawa
                self.after(1000, self.setup_game)
        else:
            self.ball.update()  # Perbarui bola
            self.after(20, self.game_loop)

    # Periksa tabrakan bola dengan objek lain
    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 10  # Tambah skor jika mengenai brick
        self.update_hud()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()
