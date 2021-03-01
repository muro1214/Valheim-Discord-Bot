import random

class TsunomakiZyanken:
    images = ['rock.png', 'scissors.png', 'paper.png']

    win_lose_table = {
        '✊': {'チョキ': 1, 'パー': -1},
        '✌️': {'パー': 1, 'グー': -1},
        '🖐️': {'グー': 1, 'チョキ': -1}
    }

    hand_table = ['グー', 'チョキ', 'パー']

    result_table = ['あなたの負け', 'あいこ', 'あなたの勝ち']

    
    def play_game(self, your_hand):
        watame_index = random.randint(0, 2)
        watame_hand = TsunomakiZyanken.hand_table[watame_index]
        result = TsunomakiZyanken.win_lose_table[your_hand].get(watame_hand, 0) + 1
        
        return f'https://www.izuna-hatsuse.net/images/tsunomaki/{TsunomakiZyanken.images[watame_index]}', TsunomakiZyanken.result_table[result] 
