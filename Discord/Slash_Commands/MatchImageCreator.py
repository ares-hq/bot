from PIL import Image, ImageDraw, ImageFont
from pathlib import Path 

class ImageCreator:
    WIDTH, HEIGHT = 800, 600
    BACKGROUND_COLOR = (43, 45, 49)  # #2B2D31
    RED_COLOR = (237, 28, 36)       # #ED1C24
    BLUE_COLOR = (0, 102, 179)      # #0066B3
    PURPLE_COLOR = (191, 64, 191)   # #BF40BF
    CATEGORY_COLOR = (154, 152, 154) # #9A989A
    INTO_THE_DEEP_COLOR = (37, 89, 164) # #2559A4
    TEXT_COLOR = (255, 255, 255)    # White
    
    base_dir = Path(__file__).parent
    font_path = base_dir / "Fonts" / "Roboto-Regular.ttf"
    font_large = ImageFont.truetype(str(font_path), 36)
    font_medium = ImageFont.truetype(str(font_path), 30)
    font_small = ImageFont.truetype(str(font_path), 17)
    
    @staticmethod
    def truncate_text(text, max_length=29):
        if type(text) is str:
            return text if len(text) <= max_length else text[:max_length - 3] + "..."
        return text
    
    @staticmethod
    def createMatchImage(red_team_1, red_team_2, blue_team_1, blue_team_2, red_team_1number, red_team_2number, blue_team_1number, blue_team_2number,red_auto, blue_auto, red_teleop, blue_teleop, 
                         red_endgame, blue_endgame, red_penalties, blue_penalties, red_final, blue_final):
        img = Image.new("RGB", (ImageCreator.WIDTH, ImageCreator.HEIGHT), color=ImageCreator.BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        # header_text = "Qualification 1 - USAZTUQ" TODO
        header_text = "Simulated Qualification"
        header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_large)
        header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
        header_position = (ImageCreator.WIDTH // 2 - header_width // 2, 10)
        draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_large)

        header_text = f"{red_team_1number} & {red_team_2number} vs. {blue_team_1number} & {blue_team_2number}"
        header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_small)
        header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
        header_position = (ImageCreator.WIDTH // 2 - header_width // 2, 60)
        draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_small)

        line_y_position = header_position[1] + header_height + 25 
        draw.line((150, line_y_position, 650, line_y_position), fill=ImageCreator.TEXT_COLOR, width=2)

        def draw_category_box(x, y, width, lines, color=ImageCreator.CATEGORY_COLOR, header_text=None, radius=0):
            if header_text:
                header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_medium)
                header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
                header_position = (x + width // 2 - header_width // 2, y - header_height - 20)
                draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_medium)

            padding = 22
            line_height = 12 #draw.textbbox((0, 0), lines[0], font=ImageCreator.font_small)[3] - draw.textbbox((0, 0), lines[0], font=ImageCreator.font_small)[1]
            total_text_height = len(lines) * line_height + padding * (len(lines) + 1)
            draw.rounded_rectangle([x, y, x + width, y + total_text_height - 1], radius=radius, fill=color)

            current_y = y + padding - 4
            for line in lines:
                if color is not ImageCreator.CATEGORY_COLOR:
                    line = ImageCreator.truncate_text(line)
                line_bbox = draw.textbbox((0, 0), line, font=ImageCreator.font_small)
                line_width = line_bbox[2] - line_bbox[0]
                line_position = (x + width // 2 - line_width // 2, current_y)
                draw.text(line_position, line, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_small)
                current_y += line_height + padding

        box_width_left = 225
        box_width_middle = 250
        box_width_right = 225
        radius = 5
        draw_category_box(25, 165, box_width_left, [red_team_1, red_team_2], ImageCreator.RED_COLOR, header_text="Red", radius=radius)
        draw_category_box(275, 165, box_width_middle, ["TEAM 1", "TEAM 2"], header_text="Alliance", radius=radius)
        draw_category_box(550, 165, box_width_right, [blue_team_1, blue_team_2], ImageCreator.BLUE_COLOR, header_text="Blue", radius=radius)

        draw_category_box(25, 320, box_width_left, [f"{red_auto}", f"{red_teleop}", f"{red_endgame}", f"{red_penalties}"], ImageCreator.RED_COLOR, radius=radius)
        draw_category_box(275, 320, box_width_middle, ["AUTO", "TELEOP", "ENDGAME", "\u2190 BLUE  PENALTIES  RED \u2192"], header_text="Score Breakdown", radius=radius)
        draw_category_box(550, 320, box_width_right, [f"{blue_auto}", f"{blue_teleop}", f"{blue_endgame}", f"{blue_penalties}"], ImageCreator.BLUE_COLOR, radius=radius)

        draw_category_box(25, 510, box_width_left, [f"{red_final}"], ImageCreator.RED_COLOR, radius=radius)
        draw_category_box(275, 510, box_width_middle, ["FINAL SCORE"], radius=radius)
        draw_category_box(550, 510, box_width_right, [f"{blue_final}"], ImageCreator.BLUE_COLOR, radius=radius)
        
        return img
    
    @staticmethod
    def createAllianceImage(team_1, team_2, team_1number, team_2number,team1_auto, team2_auto, team1_teleop, team2_teleop, 
                         team1_endgame, team2_endgame, team1_opr, team2_opr):
        img = Image.new("RGB", (ImageCreator.WIDTH, ImageCreator.HEIGHT), color=ImageCreator.BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        # header_text = "Qualification 1 - USAZTUQ" TODO
        header_text = "Simulated Alliance"
        header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_large)
        header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
        header_position = (ImageCreator.WIDTH // 2 - header_width // 2, 10)
        draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_large)

        header_text = f"{team_1number} & {team_2number}"
        header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_small)
        header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
        header_position = (ImageCreator.WIDTH // 2 - header_width // 2, 60)
        draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_small)

        line_y_position = header_position[1] + header_height + 25 
        draw.line((150, line_y_position, 650, line_y_position), fill=ImageCreator.TEXT_COLOR, width=2)

        def draw_category_box(x, y, width, lines, color=ImageCreator.CATEGORY_COLOR, header_text=None, radius=0):
            if header_text:
                header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_medium)
                header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
                header_position = (x + width // 2 - header_width // 2, y - header_height - 20)
                draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_medium)

            padding = 22
            line_height = 12 #draw.textbbox((0, 0), lines[0], font=ImageCreator.font_small)[3] - draw.textbbox((0, 0), lines[0], font=ImageCreator.font_small)[1]
            total_text_height = len(lines) * line_height + padding * (len(lines) + 1)
            draw.rounded_rectangle([x, y, x + width, y + total_text_height - 1], radius=radius, fill=color)

            current_y = y + padding - 4
            for line in lines:
                if color is not ImageCreator.CATEGORY_COLOR:
                    line = ImageCreator.truncate_text(line)
                line_bbox = draw.textbbox((0, 0), line, font=ImageCreator.font_small)
                line_width = line_bbox[2] - line_bbox[0]
                line_position = (x + width // 2 - line_width // 2, current_y)
                draw.text(line_position, line, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_small)
                current_y += line_height + padding

        box_width_left = 250
        box_width_middle = 200
        box_width_right = 250
        box_width_middle_bottom = 300
        box_width_right_bottom = 425
        radius = 5
        draw_category_box(25, 125, box_width_left, [team_1, team1_auto, team1_teleop, team1_endgame, team1_opr], ImageCreator.INTO_THE_DEEP_COLOR, radius=radius)
        draw_category_box(300, 125, box_width_middle, ["Team", "Auto OPR", "TeleOp OPR", "Endgame OPR", "Total OPR"], radius=radius)
        draw_category_box(525, 125, box_width_right, [team_2, team2_auto, team2_teleop, team2_endgame, team2_opr], ImageCreator.INTO_THE_DEEP_COLOR, radius=radius)
        
        header_text = "Estimated Alliance Score"
        header_bbox = draw.textbbox((0, 0), header_text, font=ImageCreator.font_medium)
        header_width, header_height = header_bbox[2] - header_bbox[0], header_bbox[3] - header_bbox[1]
        header_position = (ImageCreator.WIDTH // 2 - header_width // 2, 330)
        draw.text(header_position, header_text, fill=ImageCreator.TEXT_COLOR, font=ImageCreator.font_medium)

        draw_category_box(25, 375, box_width_middle_bottom, ["AUTO", "TELEOP", "ENDGAME"], radius=radius)
        draw_category_box(350, 375, box_width_right_bottom, [f"{float(team1_auto) + float(team2_auto)}", f"{float(team1_teleop) + float(team2_teleop)}", f"{float(team1_endgame) + float(team2_endgame)}"], ImageCreator.INTO_THE_DEEP_COLOR, radius=radius)

        draw_category_box(25, 520, box_width_middle_bottom, ["FINAL SCORE"], radius=radius)
        draw_category_box(350, 520, box_width_right_bottom, [f"{float(team1_opr) + float(team2_opr)}"], ImageCreator.INTO_THE_DEEP_COLOR, radius=radius)
        
        return img
    
# image = ImageCreator.createAllianceImage(
#     team="Valley X Robotics",
#     red_team_2="2",
#     blue_team_1="Valley X Robotics",
#     blue_team_2="Valley X Robotics",
#     red_team_1number=14584,
#     red_team_2number=2844,
#     blue_team_1number=1455,
#     blue_team_2number=11,
#     red_auto=5,
#     blue_auto=5,
#     red_teleop=5,
#     blue_teleop=5,
#     red_endgame=5,
#     blue_endgame=5,
#     red_penalties=0,
#     blue_penalties=0,
#     red_final=5,
#     blue_final=5
# )

# image = ImageCreator.createAllianceImage(
#     team_1="Valley X Robotics",
#     team_2="Valley X Robotics",
#     team_1number=14584,
#     team_2number=2844,
#     team1_auto="5",
#     team2_auto="5",
#     team1_teleop="5",
#     team2_teleop="5",
#     team1_endgame="5",
#     team2_endgame="5",
#     team1_opr="5",
#     team2_opr="5"
# )

# image.show()