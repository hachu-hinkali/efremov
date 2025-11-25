import pygame
import json
import math

class RecamanSequence:
    # Генерация последовательности Ракамана: a(n) = a(n-1) - n, если положительное и уникальное, иначе a(n-1) + n
    def __init__(self):
        self.sequence = [0]
        self.seen = {0}
        self.currentStep = 1

    def generateNext(self):
        lastValue = self.sequence[-1]
        candidate = lastValue - self.currentStep

        if candidate > 0 and candidate not in self.seen:
            nextValue = candidate
        else:
            nextValue = lastValue + self.currentStep

        self.sequence.append(nextValue)
        self.seen.add(nextValue)
        self.currentStep += 1

        return nextValue

    def generateTerms(self, numTerms):
        while len(self.sequence) < numTerms:
            self.generateNext()

    def getMaxValue(self):
        return max(self.sequence) if self.sequence else 0


class ArcVisualizer:
    # Отрисовка полуокружностей между значениями последовательности
    def __init__(self, config):
        self.config = config
        self.arcSettings = config["arcSettings"]

    def interpolateColor(self, index, totalArcs):
        # Градиентный переход цвета от начала к концу
        ratio = index / max(totalArcs - 1, 1)
        colorStart = self.arcSettings["colorStart"]
        colorEnd = self.arcSettings["colorEnd"]

        r = int(colorStart[0] + (colorEnd[0] - colorStart[0]) * ratio)
        g = int(colorStart[1] + (colorEnd[1] - colorStart[1]) * ratio)
        b = int(colorStart[2] + (colorEnd[2] - colorStart[2]) * ratio)

        return (r, g, b)

    def drawArc(self, surface, startVal, endVal, arcIndex, totalArcs, scale, offsetX, offsetY):
        # Рисует дугу между двумя значениями (четные индексы - вверх, нечетные - вниз)
        if startVal == endVal:
            return

        center = (startVal + endVal) / 2.0
        radius = abs(endVal - startVal) / 2.0

        # Чередование направления дуг
        direction = 1 if arcIndex % 2 == 0 else -1

        screenCenterX = offsetX + center * scale
        screenCenterY = offsetY
        screenRadius = radius * scale

        # Генерация точек полуокружности
        points = []
        segments = self.arcSettings["segments"]

        for i in range(segments + 1):
            angle = math.pi * i / segments
            if direction == -1:
                angle = -angle

            x = screenCenterX + screenRadius * math.cos(angle)
            y = screenCenterY + screenRadius * math.sin(angle)
            points.append((x, y))

        if len(points) > 1:
            color = self.interpolateColor(arcIndex, totalArcs)
            pygame.draw.lines(surface, color, False, points, self.arcSettings["strokeWeight"])


class RecamanVisualization:
    # Главный класс визуализации последовательности Ракамана
    def __init__(self, configPath="config.json"):
        with open(configPath, 'r') as f:
            self.config = json.load(f)

        pygame.init()
        self.width = self.config["windowWidth"]
        self.height = self.config["windowHeight"]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Recamán's Sequence Visualization")

        self.sequence = RecamanSequence()
        self.visualizer = ArcVisualizer(self.config)

        self.currentArc = 0
        self.maxTerms = self.config["maxTerms"]
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        self.sequence.generateTerms(self.maxTerms)

        self.scale = 1.0
        self.offsetX = 0.0
        self.offsetY = self.height * self.config["numberLineSettings"]["yPosition"]

        self.calculateScaling()

    def calculateScaling(self):
        # Автоматическое масштабирование для вмещения всей последовательности
        if not self.config["autoScaling"]["enabled"]:
            return

        maxValue = self.sequence.getMaxValue()
        padding = self.config["autoScaling"]["padding"]

        if maxValue > 0:
            self.scale = (self.width - 2 * padding) / maxValue
            self.offsetX = padding

    def drawNumberLine(self):
        lineY = self.offsetY
        color = tuple(self.config["numberLineSettings"]["color"])

        pygame.draw.line(self.screen, color, (0, lineY), (self.width, lineY), 2)

        markerSize = self.config["numberLineSettings"]["markerSize"]
        for i, value in enumerate(self.sequence.sequence[:self.currentArc + 1]):
            x = self.offsetX + value * self.scale
            pygame.draw.circle(self.screen, color, (int(x), int(lineY)), markerSize)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def reset(self):
        self.currentArc = 0

    def update(self):
        if not self.paused and self.currentArc < len(self.sequence.sequence) - 1:
            self.currentArc += 1

    def draw(self):
        bgColor = tuple(self.config["backgroundColor"])
        self.screen.fill(bgColor)

        self.drawNumberLine()

        for i in range(self.currentArc):
            startVal = self.sequence.sequence[i]
            endVal = self.sequence.sequence[i + 1]
            totalArcs = len(self.sequence.sequence) - 1

            self.visualizer.drawArc(self.screen, startVal, endVal, i, totalArcs,
                                   self.scale, self.offsetX, self.offsetY)

        self.drawInstructions()

        pygame.display.flip()

    def drawInstructions(self):
        font = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Pause/Resume",
            "R: Reset",
            "ESC: Exit",
            f"Arc: {self.currentArc}/{len(self.sequence.sequence) - 1}"
        ]

        y = 10
        for text in instructions:
            surface = font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (10, y))
            y += 25

    def run(self):
        while self.running:
            self.handleEvents()
            self.update()
            self.draw()
            self.clock.tick(self.config["animationSpeed"])

        pygame.quit()


visualization = RecamanVisualization()
visualization.run()
