from PIL import Image, ImageDraw

def create_valid_icon():
    # We need to pack multiple sizes into one file for Windows to accept it properly
    icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    images = []

    for size in icon_sizes:
        # Create a transparent image
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw Red Camera Body (Rectangle)
        # Scale coordinates based on size
        w, h = size
        draw.rectangle(
            [w*0.1, h*0.3, w*0.9, h*0.8], 
            fill=(220, 40, 40), outline=None
        )
        
        # Draw Lens (White Circle)
        draw.ellipse(
            [w*0.25, h*0.35, w*0.6, h*0.75],
            fill=(255, 255, 255)
        )
        
        # Draw Tally Light (Top bump)
        draw.rectangle(
            [w*0.3, h*0.15, w*0.7, h*0.3],
            fill=(255, 0, 0)
        )
        
        images.append(img)

    # Save as a proper ICO file containing all sizes
    images[0].save('fixed_icon.ico', format='ICO', sizes=icon_sizes, append_images=images[1:])
    print("Success! 'fixed_icon.ico' created.")

if __name__ == "__main__":
    create_valid_icon()