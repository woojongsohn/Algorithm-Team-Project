from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.patches as mpatches
import heapq

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 그래프 초기화
graph = {
    '1': [('2', 3), ('4', 4), ('6', 1), ('8', 3), ('12', 2), ('14', 7), ('15', 2), ('16', 1), ('17', 3)],
    '2': [('1', 10), ('3', 1), ('12', 2), ('15', 2), ('17', 2)],
    '3': [('2', 1), ('5', 2), ('15', 2)],
    '4': [('1', 6), ('7', 3), ('8', 3), ('12', 2), ('17', 2), ('22', 2)],
    '5': [('3', 2), ('6', 1), ('15', 1), ('16', 1)],
    '6': [('1', 3), ('5', 1), ('12', 1), ('15', 1), ('16', 2)],
    '7': [('4', 2), ('8', 2), ('10', 1), ('22', 2)],
    '8': [('1', 3), ('4', 3), ('7', 2), ('10', 3), ('12', 3), ('15', 3)],
    '9': [('18', 8), ('19', 3), ('20', 1), ('21', 1)],
    '10': [('7', 1), ('8', 2), ('13', 1)],
    '11': [('13', 4), ('14', 3), ('18', 5)],
    '12': [('1', 3), ('2', 2), ('4', 2), ('6', 3), ('8', 4), ('15', 2), ('17', 2)],
    '13': [('8', 3), ('10', 1), ('11', 8), ('14', 7)],
    '14': [('1', 5), ('11', 4), ('13', 6)],
    '15': [('2', 2), ('3', 2), ('5', 1), ('6', 1), ('12', 2), ('17', 3)],
    '16': [('1', 2), ('5', 1), ('6', 2)],
    '17': [('2', 2), ('4', 2), ('12', 2), ('15', 3), ('22', 2)],
    '18': [('9', 6), ('11', 3), ('19', 5), ('20', 4)],
    '19': [('9', 2), ('18', 5), ('20', 1)],
    '20': [('9', 1), ('18', 4), ('19', 1), ('21', 1)],
    '21': [('9', 1), ('20', 1)],
    '22': [('4', 2), ('7', 4), ('17', 2)]
}

# 노드 위치 지정 (캠퍼스 지도 좌표)
pos = {
    '1': (708, 278), '2': (535, 70), '3': (628, 61),
    '4': (366, 244), '5': (715, 125), '6': (645, 169),
    '7': (280, 351), '8': (470, 329), '9': (253, 464),
    '10': (345, 410), '11': (695, 490), '12': (525, 161),
    '13': (383, 427), '14': (695, 421), '15': (596, 130),
    '16': (799, 185), '17': (356, 140), '18': (538, 535),
    '19': (231, 555), '20': (186, 511), '21': (163, 453),
    '22': (236, 200)
}

def dijkstra(graph, start, target):
    pq = []
    heapq.heappush(pq, (0, start))
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_node == target:
            break
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    return path, distances[target]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        source = request.form['source']
        target = request.form['target']
        try:
            shortest_path, shortest_distance = dijkstra(graph, source, target)

            # 시각화 설정
            fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
            try:
                img = Image.open("static/final_map.png")
                ax.imshow(img, extent=[0, 900, 0, 600])
            except FileNotFoundError:
                print("Background image not found. Please check the file path.")

            # 모든 엣지 그리기
            for node, neighbors in graph.items():
                for neighbor, weight in neighbors:
                    x1, y1 = pos[node]
                    x2, y2 = pos[neighbor]
                    # 회색 실선으로 모든 엣지 표시
                    ax.arrow(x1, y1, x2 - x1, y2 - y1,
                             color='dimgray', alpha=0.6, width=0.5, head_width=10, length_includes_head=True,
                             linestyle='-', linewidth=1.0)

            # 최단 경로 강조 (빨간 화살표)
            for i in range(len(shortest_path) - 1):
                current = shortest_path[i]
                next_node = shortest_path[i + 1]
                x1, y1 = pos[current]
                x2, y2 = pos[next_node]
                ax.arrow(x1, y1, x2 - x1, y2 - y1,
                         color='red', width=0.8, head_width=12, length_includes_head=True,
                         linestyle='-', linewidth=2, zorder=5)

            # 모든 노드 그리기
            for node, (x, y) in pos.items():
                ax.scatter(x, y, s=300, color='white', edgecolor='dimgray', linewidth=2, zorder=10)  # 노드 원
                ax.text(x, y, node, fontsize=8, ha='center', va='center', fontweight='bold', zorder=15)  # 노드 번호

            # 최단 경로 상의 엣지 가중치 강조 (원으로 감싸기)
            for i in range(len(shortest_path) - 1):
                current = shortest_path[i]
                next_node = shortest_path[i + 1]
                weight = graph[current][[n[0] for n in graph[current]].index(next_node)][1]  # 가중치 가져오기
                # 엣지 중간 위치 계산
                midpoint = ((pos[current][0] + pos[next_node][0]) / 2, (pos[current][1] + pos[next_node][1]) / 2)
                # 가중치를 원 안에 표시
                circle = mpatches.Circle(midpoint, 12, color='black', zorder=9)
                ax.add_patch(circle)
                ax.text(midpoint[0], midpoint[1], weight, color='white', fontsize=12, ha='center', va='center', zorder=10)

            ax.axis('off')  # 축 제거
            plt.savefig("static/shortest_path.png", bbox_inches="tight")
            plt.close()

            return render_template('index.html', shortest_path=shortest_path, shortest_distance=shortest_distance, image="/static/shortest_path.png")
        except Exception as e:
            return render_template('index.html', error=str(e))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
