from scene import *
#import pathlib 
import sound
import random

standing = Texture('Graphicassets/resized/standingimage.png')

walking = [Texture('Graphicassets/resized/walkingclosedfeet.png'),Texture ('Graphicassets/resized/walkingopenfeet.png')]

hit_texture = Texture('Graphicassets/resized/hitbyrock.png')

class Coin(SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'plf:Item_CoinGold', **kwargs)
		
class Meteor(SpriteNode):
	def __init__(self, **kwargs):
		img = random.choice(['spc:MeteorBrownBig1','spc:BoltBronze','spc:MeteorGrayBig1'])
		SpriteNode.__init__(self, img, **kwargs)


class Boomtown(Scene):
	
	def setup(self):
		self.background_color = "#3a5d65"
		ground = Node(parent=self)
		x = 0
		while x <= self.size.w +64:
			stone = SpriteNode('plf:Ground_DirtMid', position=(x,10))
			ground.add_child(stone)
			x += 64
 		#create player sprite
		self.player = SpriteNode('Graphicassets/standing.png')
		#position center and just 
		self.player.position = (self.size.w/2, 41)
 		#anchor point 
		self.player.anchor_point = (0.5, 0)
		#attach player to the ground
		ground.add_child(self.player)
		#add score
		self.label_score = LabelNode('0', ('futura',40), parent=self)
		self.label_score.position = (self.size.w / 2, self.size.h -40)
		self.list_of_items = []
		self.list_of_lasers = []
		self.new_game()
		
	def new_game(self):
		for items in self.list_of_items:
			items.remove_from_parent()
		self.score = 0
		self.walk_state = -1
		self.list_of_items = []
		self.list_of_lasers = []
		self.game_over = False
		self.label_score.text = '0'
		laser = False
		self.player.position = self.size.w / 2, 35
		self.speed = 1
		self.player.texture = standing
		
	def update(self):#how many items drops
		if self.game_over:
			return
		if random.random() < .05:
			self.spawn_items()
		self.update_player()
		#look for collisions
		self.collision_with_items()
		self.collisions_with_lasers()
		
	def update_player(self):
		g = gravity()
		
		self.player.x_scale = ((g.x > 0) - (g.x < 0))
		
		if abs(g.y) > 0.05:
			speed = g.y * 45
			x = self.player.position.x
			x = max(0, min(self.size.w, x + speed)) 
			self.player.position = x, 35
			step = int(self.player.position.x / 40) % 2
			if step != self.walk_state:
				self.player.texture = walking[step]
				sound.play_effect('rpg:Footstep00', 0.05, 1.0 + .5 * g.x)
				self.walk_state = step
	
		else:
			self.player.texture = standing
			self.walk_state = -1
					
	def spawn_items(self):
			if random.random() < 0.4:
				meteor = Meteor(parent=self)
				meteor.position = random.uniform(100, self.size.w),self.size.h
				duration = random.uniform(2,4)
				meteor.run_action(
					Action.sequence(
						Action.move_to(0,-1000, duration), 
						Action.remove()
						)
					)
				self.list_of_items.append(meteor)
			
			else:
				coin = Coin(parent=self)
				coin.position = random.uniform(20, self.size.w), self.size.h 
				duration = random.uniform(2,4) 
				coin.run_action(
					Action.sequence(
						Action.move_by(0,-1000, duration), 
						Action.remove()
						)
					)
				#List of coins falling
				self.list_of_items.append(coin)
									
#coins collisions maybe collision location as we?
	def collision_with_items(self):
		p_box = Rect(self.player.position.x-20, 32, 40, 65)
		for item in self.list_of_items:
			if item.frame.intersects(p_box):
				if isinstance(item, Coin):
					sound.play_effect('arcade:Coin_2')
					item.remove_from_parent()
					self.list_of_items.remove(item)
					self.score += 10
					self.label_score.text = str(self.score)
				else:
					self.player_hit()
	
	def collisions_with_lasers(self):
		for laser in self.list_of_lasers:
			if not laser.parent:
				self.list_of_lasers.remove(laser)
				continue
			for item in self.list_of_items:
				if not isinstance(item, Meteor):
					continue	
				if laser.position in item.frame:
					sound.play_effect('arcade:Explosion_6', 0.2)
					self.list_of_items.remove(item)
					self.list_of_lasers.remove(laser)
					item.remove_from_parent()
					laser.remove_from_parent()
					self.score += 20
					self.label_score.text = str(self.score)
					break			
	
	def player_hit(self):
		self.game_over = True
		sound.play_effect('arcade:explosion_6')
		self.player.texture = hit_texture
		#This failed once ran at end of game. self.run_action(Action.move_by(0-150))
		
		self.run_action(Action.sequence(
			Action.wait(2*self.speed), Action.call(self.new_game)))
													
	def touch_began(self, Touch):
		#load the sprite
		laser = SpriteNode('plf:SwordSilver', 
			position=self.player.position, 
			z_position= -1, 
			parent=self)
		
		#move the laser
		laser.run_action(Action.sequence(
			Action.move_by(0,1000), 
			Action.remove()))
		
		#Add sounds
		sound.play_effect('arcade:Laser_2')
		self.list_of_lasers.append(laser)
		
			
	
run(Boomtown(), PORTRAIT)
