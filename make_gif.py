# -*- coding: gbk -*- 
import imageio
import os
import os.path as osp


def img2gif(img_dir, gif_path, duration):
    """

    :param img_dir: 包含图片的文件夹
    :param gif_path: 输出的gif的路径
    :param duration: 每张图片切换的时间间隔，与fps的关系：duration = 1 / fps
    :return:
    """
    frames = []
    for idx in sorted(os.listdir(img_dir), key=lambda x:int(x[:-4])):
        img = osp.join(img_dir, idx)
        # print(img)
        frames.append(imageio.imread(img))
    imageio.mimsave(gif_path, frames, 'GIF', duration=duration)
    print('Finish changing!')

def makedir(path):
    if os.path.exists(path):
        return
    else:
        os.makedirs(path)

if __name__ == '__main__':
    img_dir = '/public/zhaoboyao/interpreter/cifar/adv_wmg/images/0.9_15_10_1_0.4_25_0.99_128_2500_2022-11-14 17:44:19'
    filename = '/public/zhaoboyao/interpreter/cifar/adv_wmg/gifs/0.9_15_10_1_0.4_25_0.99_128_2500_2022-11-14 17:44:19/'
    makedir(filename)
    gif_path = filename + 'output.gif'
    img2gif(img_dir=img_dir, gif_path=gif_path, duration=0.001)
