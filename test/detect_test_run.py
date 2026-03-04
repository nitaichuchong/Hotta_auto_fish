from UI.detect_test_annotation_ui import DetectionUI


def annotation_test():
    annotation = DetectionUI()
    annotation.run()


if __name__ == '__main__':
    """
    为了避免循环依赖将启动分开写了，最开始想过要不要用这个作为所有测试的入口，
    但是已经写得很头大了，就不要搞那么高的集成度
    """
    annotation_test()
