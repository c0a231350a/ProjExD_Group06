"""
ボスの攻撃を画面買いに出ないようにするための反射
＋機能として反射するたびに攻撃玉のサイズをランダムで変更
"""
import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Gravity(pg.sprite.Sprite):

    def __init__(self,life):
        super().__init__()
        self.life = life
        self.image = pg.Surface((1100, 650))
        pg.draw.rect(self.image, (0,0,0), (0, 0, 1100, 650))
        self.image.set_alpha(192)
        self.rect = self.image.get_rect()

    def update(self):
        if self.life >= 0:
            self.life -= 1
        else:
            self.kill()

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = (100,HEIGHT/2)
        self.speed = 10
        self.state = "normal"  # 状態変数: "normal" or "hyper"
        self.hyper_life = 0  # 無敵状態の残りフレーム数
        self.hp =1000                    #自キャラの総HP
        self.h_rect = 500, HEIGHT-50     #HP表示される座標
        self.h_name = "You"        #自キャラの名前表記

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        """
        
        # 左SHIFTが押されていたら速度を20に設定
        if key_lst[pg.K_LSHIFT]:
            self.speed = 20
        else:
            self.speed = 10
            
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

        # 無敵状態の発動チェック
        if key_lst[pg.K_RSHIFT]  and self.state == "normal" and MP.mp > 200:  # 発動条件：mpが200より大 and score.value >= 100
            self.state = "hyper"
            self.hyper_life = 500  # 発動時間：500フレーム
            self.image = pg.transform.laplacian(self.image)  # 画像を変換

        # 無敵状態の持続
        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.laplacian(self.image)  # 画像を変換
            if self.hyper_life <= 0:
                self.state = "normal"  # 無敵状態終了
                self.image = self.imgs[self.dire]  # 画像を元に戻す

        screen.blit(self.image, self.rect)
        


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255), (0, 0, 0)]

    def __init__(self, emy: "Enemy", bird: Bird, vx, vy):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(30, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = (255,0,0)
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = vx, vy  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 10  #球速10
        self.bounce_count = 0  # 反射回数をカウント

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)

        # 壁での反射処理
        yoko, tate = check_bound(self.rect)
        if not yoko or not tate:
            self.vx *= -1 if not yoko else 1  # 横方向の速度を反転
            self.vy *= -1 if not tate else 1  # 縦方向の速度を反転
            self.bounce_count += 1  # 反射回数を増加
            self.change_size()  # 大きさをランダムに変更

        # 反射回数が1000回を超えたら爆弾を削除
        if self.bounce_count > 1000:
            self.kill()

    def change_size(self):
        """
        壁に当たるたびにランダムな大きさに変更
        """
        rad = random.randint(5, 50)  # 新しい半径をランダムに決定
        color = random.choice(Bomb.colors)
        self.image = pg.Surface((2 * rad, 2 * rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=self.rect.center)  # 中心位置を維持して更新

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle0=0):
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class NeoBeam(pg.sprite.Sprite):
    """
    追加機能６：複数の弾幕の生成に関するクラス
    """
    def __init__(self, bird:Bird, num=5):
        self.bird = bird
        self.num = num

    def gen_beams(self) :
        beams = []
        angle_range = (-50, 51)
        angle_step = (angle_range[1] - angle_range[0]) // self.num  
        for i in range(self.num):
            angle = angle_range[0] + i * angle_step  
            beams.append(Beam(self.bird, angle))  
        return beams


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = pg.image.load(f"fig/alien100.png")
    
    def __init__(self):
        super().__init__()
        self.image = __class__.imgs
        self.rect = self.image.get_rect()
        self.rect.center = 900, 0
        self.vx, self.vy = 0, +6
        self.bound = WIDTH/2  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル
        self.hp = 2500               #相手の総HP
        self.h_rect = 200, 50        #相手のHP表記の座標
        self.h_name = "BOSS"         #相手の名前表記

    def update(self):
        if self.state == "down":
            if self.rect.centery >= self.bound:
                self.vy = random.choice([-3,3])
                self.state = "move"
            else:
                self.rect.move_ip(self.vx, self.vy)
        elif self.state == "move":
            self.rect.move_ip(self.vx,self.vy)
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.vx *= -1
            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.vy *= -1


class HP(pg.sprite.Sprite):
    """
    コウカトンとボスのHPを計算、表示させるクラス
    """

    def __init__(self,hp_value,a_name,a_center):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = hp_value
        self.a_name = a_name
        self.image = self.font.render(f"{self.a_name} HP: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = a_center
        

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"{self.a_name} HP: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

class MP:
    """
    mpの初期値を設定する
    mpを5フレームごとに回復させる
    """
    def __init__(self):
        self.mp = 300 #mpの初期値
        self.font = pg.font.Font(None,25)
        self.color = (0, 0, 255)
        self.image = self.font.render(f"MP: {self.mp}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 0,0
        
    def update(self,tmr,screen: pg.Surface):
        #mpの自然回復
        if self.mp < 300 and tmr%5 == 0: #mpの300未満の時、5フレームごとにmpを+1
            self.mp += 1
        
        #MP残量表示
        self.image = pg.Surface((300,10))
        self.rect = self.image.get_rect()
        self.rect.center = 250,575
        self.image = self.font.render(f"MP: {self.mp}", 0, self.color)
        screen.blit(self.image, self.rect)
        
        #空のMP容量
        self.image = pg.Surface((300,10))
        self.rect = self.image.get_rect()
        self.rect.center = 250, 560
        pg.draw.rect(self.image, (0,0,0), (200, 200, 300, 10))
        screen.blit(self.image, self.rect)

        #MP残量
        self.image = pg.Surface((self.mp,10))
        self.rect = self.image.get_rect()
        self.rect.center = self.mp/2+100, 560
        pg.draw.rect(self.image, (0,0,255), (0, 0, self.mp, 10))
        screen.blit(self.image, self.rect)


class EMP:
    def __init__(self,emys: pg.sprite.Group,Bombs: pg.sprite.Group,screen : pg.surface):
        for emy in emys:
            emy.interval = float("inf")
            emy.image =pg.transform.laplacian(emy.image)
            emy.image.set_colorkey((0,0,0))
        for bomb in Bombs:
            bomb.speed /=2
            bomb.state = "inactive"
        
        self.image = pg.Surface((WIDTH,HEIGHT))
        pg.draw.rect(self.image, (255,255,0), (0, 0, WIDTH, HEIGHT))
        self.image.set_alpha(100)
        screen.blit(self.image,[0,0])
        pg.display.update()
        time.sleep(0.05)

        
class Shield(pg.sprite.Sprite):
    """
    シールドに関するクラス
    """
    def __init__(self, bird: Bird, life: int):
        super().__init__()
        k_rect = bird.rect
        self.image = pg.Surface((20, k_rect.height*2))
        self.rect = self.image.get_rect()
        color = (0, 0, 255)
        pg.draw.rect(self.image, color, (0, 0, 20, k_rect.height*2))
        vx, vy = bird.dire
        angle = math.degrees(math.atan2(-vy, vx))
        self.image = pg.transform.rotozoom(self.image, angle, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

        if vx == 0 and vy != 0:
            self.rect.centerx = bird.rect.centerx
            self.rect.centery = bird.rect.centery + vy * (k_rect.height + 10)
        elif vx != 0 and vy == 0:
            self.rect.centerx = bird.rect.centerx + vx * (k_rect.width + 10)
            self.rect.centery = bird.rect.centery
        else:
            self.rect.centerx = bird.rect.centerx + vx * (k_rect.width + 10)
            self.rect.centery = bird.rect.centery + vy * (k_rect.height + 10)

        self.life = life

    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    beam_f_or_t=False     #beamで攻撃した時のtrue_false判定
    gravity_f_or_t=False  #gravityで攻撃した時のtrue_false判定

    mp = MP()
    state = "inactive"

    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravity = pg.sprite.Group()
    shields = pg.sprite.Group()

    data_enemy = Enemy()

    enemy_hp = HP(data_enemy.hp,data_enemy.h_name,data_enemy.h_rect)
    bird_hp = HP(bird.hp,bird.h_name,bird.h_rect)


    
    tmr = 0
    clock = pg.time.Clock()
    while True:
        if state == "active":
            key_lst = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return 0 
                
                if event.type == pg.KEYDOWN and key_lst[pg.K_LSHIFT] and event.key == pg.K_SPACE and mp.mp > 30:
                    mp.mp -= 30   
                    neo_beam = NeoBeam(bird,5) 
                    beams.add(*neo_beam.gen_beams())
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE and mp.mp > 5:
                    mp.mp -= 5
                    beams.add(Beam(bird))
                # if event.type == pg.KEYDOWN and event.key == pg.K_e:
                    # EMP(emys,bombs,screen)

                if event.type  == pg.KEYDOWN and event.key == pg.K_0:
                    #if score.value > 200:
                    if mp.mp > 50:
                        gravity.add(Gravity(50))
                        mp.mp -= 50
                        
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB and  mp.mp > 75:
                    mp.mp -= 75
                    shields.add(Shield(bird, 400))
            screen.blit(bg_img, [0, 0])   

            if tmr == 200:  # 200フレームに1回，敵機を出現させる
                emys.add(Enemy())

            if tmr == 400:  # 400フレームに1回，敵機を出現させる
                emys.add(Enemy())

            if tmr == 600:  # 600フレームに1回，敵機を出現させる
                emys.add(Enemy())

            for emy in emys:
                if tmr%emy.interval == 0:
                    num = 3
                    angles = [i - num//2 for i in range(num)]
                    angle_step = 90/num
                    vx, vy = calc_orientation(emy.rect, bird.rect)
                    angle = math.degrees(math.atan2(-vy, vx))
                    for i in range(num):
                        vx = math.cos(math.radians(angle + angles[i] * angle_step))
                        vy = -math.sin(math.radians(angle + angles[i] * angle_step))
                        bombs.add(Bomb(emy, bird, vx, vy))


            for emy in pg.sprite.groupcollide(emys, beams, beam_f_or_t, True).keys():
                enemy_hp.value -=50    #攻撃を自キャラが相手に行ったらHPを50減らす
                if enemy_hp.value < 0:
                    enemy_hp.value=0
                if 0 <= enemy_hp.value <=50: #beamで残り攻撃回数1回で相手を倒せるHP残量になったらbeam_f_or_t=Trueにする
                    # beam_f_or_t=True
                    if enemy_hp.value <=0:  #相手のHPがゼロになったら演出を行う
                        for emy in emys:
                            emy.kill()
                            exps.add(Explosion(emy, 100))  # 爆発エフェクト
                        bird.change_img(6, screen)  # こうかとん喜びエフェクト
                        fonto = pg.font.Font(None, 80) 
                        txt = fonto.render("Game Clear!!", True, (255, 0, 0))
                        txt_rect = txt.get_rect()
                        screen.blit(txt, [(WIDTH-txt_rect.width)/2, (HEIGHT-txt_rect.height)/2])
                        pg.display.update()
                        time.sleep(5)
                        return



            for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                        
            for bomb in pg.sprite.groupcollide(bombs, shields, True, False).keys():
                    exps.add(Explosion(bomb, 50))

            for emy in pg.sprite.groupcollide(emys, gravity, gravity_f_or_t, False):
                enemy_hp.value -=1   #攻撃を自キャラが相手に行ったらHPを1減らす
                if enemy_hp.value < 0:
                    enemy_hp.value=0
                if 0 <= enemy_hp.value <=1: #gravityで残り攻撃回数1回で相手を倒せるHP残量になったらgravity_f_or_t=Trueにする
                    # gravity_f_or_t=True
                    if enemy_hp.value <=0:  #相手のHPがゼロになったら演出を行う
                        for emy in emys:
                            emy.kill()
                            exps.add(Explosion(emy, 100))  # 爆発エフェクト
                        bird.change_img(6, screen)  # こうかとん喜びエフェクト
                        fonto = pg.font.Font(None, 80) 
                        txt = fonto.render("Game Clear!!", True, (255, 0, 0))
                        txt_rect = txt.get_rect()
                        screen.blit(txt, [(WIDTH-txt_rect.width)/2, (HEIGHT-txt_rect.height)/2])
                        pg.display.update()
                        time.sleep(5)
                        return

                for bomb in pg.sprite.groupcollide(bombs, gravity, True, False):
                    exps.add(Explosion(bomb, 50))

            if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
                if bird.state != "hyper":  # 無敵状態でない場合
                    bird_hp.value -=100 #相手から攻撃を受けたら自キャラのHPを100減らす
                    if bird_hp.value <=0:  #HPが0になったら演出
                        bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                        pg.display.update()
                        time.sleep(2)
                        return
            gravity.update()
            gravity.draw(screen)
            bird.update(key_lst, screen)
            beams.update()
            beams.draw(screen)
            emys.update()
            emys.draw(screen)
            bombs.update()
            bombs.draw(screen)
            exps.update()
            exps.draw(screen)
            enemy_hp.update(screen)
            bird_hp.update(screen)
            shields.draw(screen)
            shields.update()
            mp.update(tmr,screen)
            pg.display.update()

            tmr += 1
            clock.tick(50)
        elif state == "inactive":
            fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)
            txt = fonto.render("ゲームを始めるにはSを押してね", True, (255, 0, 0))
            txt_rct = txt.get_rect()
            screen.blit(bg_img, [0, 0])
            screen.blit(txt, [(WIDTH-txt_rct.width)/2, (HEIGHT-txt_rct.height)/2])
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return 0
                if event.type == pg.KEYDOWN and event.key == pg.K_s:
                    state = "active"
            pg.display.update()

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
