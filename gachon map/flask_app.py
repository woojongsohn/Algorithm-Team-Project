# networkX 라이브러리를 사용한 다익스트라

from flask import Flask, render_template, request
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.patches as mpatches

# Flask 애플리케이션 초기화
app = Flask(__name__)

# 방향 그래프 생성
G = nx.DiGraph()

# 그래프의 엣지와 가중치 정의
edges_with_weights = [
    # (출발 노드, 도착 노드, 가중치) 형식으로 엣지 추가
    ('1', '2', 3), ('1', '4', 4), ('1', '6', 1), ('1', '8', 3), ('1', '12', 2), ('1', '14', 7), ('1', '15', 2), ('1', '16', 1), ('1', '17', 3),
    ('2', '1', 10), ('2', '3', 1), ('2', '12', 2), ('2', '15', 2), ('2', '17', 2),
    ('3', '2', 1), ('3', '5', 2), ('3', '15', 2),
    ('4', '1', 6), ('4', '7', 3), ('4', '8', 3), ('4', '12', 2), ('4', '17', 2), ('4', '22', 2),
    ('5', '3', 2), ('5', '6', 1), ('5', '15', 1), ('5', '16', 1),
    ('6', '1', 3), ('6', '5', 1), ('6', '12', 1), ('6', '15', 1), ('6', '16', 2),
    ('7', '4', 2), ('7', '8', 2), ('7', '10', 1), ('7', '22', 2),
    ('8', '1', 3), ('8', '4', 3), ('8', '7', 2), ('8', '10', 3), ('8', '12', 3), ('8', '15', 3),
    ('9', '18', 8), ('9', '19', 3), ('9', '20', 1), ('9', '21', 1),
    ('10', '7', 1), ('10', '8', 2), ('10', '13', 1),
    ('11', '13', 4), ('11', '14', 3), ('11', '18', 5),
    ('12', '1', 3), ('12', '2', 2), ('12', '4', 2), ('12', '6', 3), ('12', '8', 4), ('12', '15', 2), ('12', '17', 2),
    ('13', '8', 3), ('13', '10', 1), ('13', '11', 8), ('13', '14', 7),
    ('14', '1', 5), ('14', '11', 4), ('14', '13', 6),
    ('15', '2', 2), ('15', '3', 2), ('15', '5', 1), ('15', '6', 1), ('15', '12', 2), ('15', '17', 3),
    ('16', '1', 2), ('16', '5', 1), ('16', '6', 2),
    ('17', '2', 2), ('17', '4', 2), ('17', '12', 2), ('17', '15', 3), ('17', '22', 2),
    ('18', '9', 6), ('18', '11', 3), ('18', '19', 5), ('18', '20', 4),
    ('19', '9', 2), ('19', '18', 5), ('19', '20', 1),
    ('20', '9', 1), ('20', '18', 4), ('20', '19', 1), ('20', '21', 1),
    ('21', '9', 1), ('21', '20', 1),
    ('22', '4', 2), ('22', '7', 4), ('22', '17', 2)
]

# 그래프에 가중치가 있는 엣지 추가
G.add_weighted_edges_from(edges_with_weights)

# 노드 위치 지정 (캠퍼스 지도 좌표)
pos = {
    '1': (708, 278), '2': (535, 70), '3': (628, 61), 
    '4': (366, 244), '5': (715, 125),'6': (645, 169), 
    '7': (280, 351), '8': (470, 329), '9': (253, 464), 
    '10': (345, 410),'11': (695, 490), '12': (525, 161), 
    '13': (383, 427), '14': (695, 421), '15': (596, 130),
    '16': (799, 185), '17': (356, 140), '18': (538, 535), 
    '19': (231, 555), '20': (186, 511),'21': (163, 453), 
    '22': (236, 200)
}

# Flask 라우트 설정
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 사용자가 데이터를 제출한 경우
        source = request.form['source']  # 시작 노드
        target = request.form['target']  # 도착 노드
        try:
            # 다익스트라 알고리즘을 사용하여 최단 경로와 거리 계산
            shortest_path = nx.dijkstra_path(G, source, target)
            shortest_distance = nx.dijkstra_path_length(G, source, target)

            # 경로와 가중치를 단계별로 저장
            steps = []
            cumulative_weight = 0
            cumulative_weights_str = ""
            for i in range(1, len(shortest_path)):
                # 현재 경로의 가중치 가져오기
                weight = G[shortest_path[i-1]][shortest_path[i]]['weight']
                cumulative_weight += weight  # 가중치를 누적
                if i == 1:
                    cumulative_weights_str = f"{weight}"  # 첫 번째 단계의 가중치
                else:
                    cumulative_weights_str += f" + {weight}"  # 누적 가중치 문자열

                # 단계별 경로와 가중치 저장
                step = f"Step {i} : {shortest_path[i-1]} -> {shortest_path[i]} (weight : {cumulative_weights_str})"
                steps.append(step)

            # 최단 경로 시각화
            fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
            try:
                # 배경 지도 이미지 로드
                img = Image.open("static/final_map.png")
                ax.imshow(img, extent=[0, 900, 0, 600])
            except FileNotFoundError:
                print("Background image not found. Please check the file path.")

            # 그래프 그리기
            nx.draw(
                G, pos, ax=ax, with_labels=True, node_color='white', font_weight='bold',
                font_size=8, node_size=300, edge_color='dimgray', arrowsize=7,
                node_shape='o', linewidths=2, edgecolors='dimgray'
            )

            # 최단 경로를 강조 (빨간색 선으로 표시)
            path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=path_edges, edge_color='red', width=2)

            # 최단 경로 상의 엣지 가중치 시각화
            for edge in path_edges:
                weight = G[edge[0]][edge[1]]['weight']  # 엣지의 가중치
                # 엣지 중간 위치 계산
                midpoint = ((pos[edge[0]][0] + pos[edge[1]][0]) / 2, (pos[edge[0]][1] + pos[edge[1]][1]) / 2)
                # 엣지 위에 가중치를 원으로 표시
                circle = mpatches.Circle(midpoint, 12, color='black', zorder=9)
                ax.add_patch(circle)
                ax.text(midpoint[0], midpoint[1], weight, color='white', fontsize=12, ha='center', va='center', zorder=10)

            # 축 제거
            ax.axis('off')
            # 결과 이미지를 저장
            output_path = 'static/shortest_path.png'
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()

            # 결과를 웹 페이지에 전달
            return render_template('index.html', shortest_path=shortest_path, shortest_distance=shortest_distance, steps=steps, image='/' + output_path)
        except Exception as e:
            print(f"Error: {e}")
            return render_template('index.html', error=str(e))
    return render_template('index.html')  # 기본 페이지 렌더링

if __name__ == '__main__':
    # Flask 애플리케이션 실행
    app.run(debug=True, threaded=False)
