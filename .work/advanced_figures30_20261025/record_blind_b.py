from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parent
cards=json.loads((ROOT/'blind_cards_a.json').read_text(encoding='utf-8'))['cards']
answers={
1:('B','三个黑点分主体运动：内圈黑点逐次逆时针移一格；外圈两个黑点分别顺时针移一格和两格，下一幅内点为左上，外点在右边相邻两点。',.97,[]),
2:('D','先找外轮廓唯一对称轴：三角形竖轴、风筝四边形斜轴、箭头横轴，外轴每次顺时针45°；内部Z折线每次逆时针45°。右组第三图应为斜箭头及对应Z方向。',.92,['最初未认出风筝形对称轴，只凭边数和内部折线会留下B、D；重新沿风筝相邻等边寻找斜轴后自行消除了该疑问。']),
3:('A','每行先把第一幅黑格整体顺时针旋转90°，再和保持原位的第二幅逐格求异。第三行计算得到A。',.97,[]),
4:('C','每格所有多边形的直角总数等于封闭图形数加黑点数。左组为5=2+3、7=3+4、4=2+2，右组亦一致；候选C的直角为3+3+1=7，等于3个图形加4个点。',.84,['斜放多边形的直角需细看；我用原图像素的轮廓向量辅助估计，未读取作者的几何源数据。图像粗化会增加人工辨认负担，但未恢复出另一个同样自然的正确候选。']),
5:('D','每格主体方框内部的最小封闭面数等于主体框外连接短线的数量。前三图分别3、6、4，后两图7、5，D项为5面和5条外接短线。内部不封面的短线不能算新面。',.96,[]),
6:('B','每幅由两个线图组成，最少笔画总数依次为2、3、4、2、3，下一幅应4笔。B为一个3笔图加一个闭合一笔图，其余三项均3笔。',.96,[]),
7:('A','忽略最外排版框，找各图最大封闭面，即内层多边形。①③⑥仅中心对称，②④⑤仅轴对称。外层小边和连接线是干扰。',.92,['此题需要先选定最大面；按全图外轮廓看不出同样稳定分法。']),
8:('C','只看黑色小格组成的子图，①④⑤是中心对称而无对称轴；②③⑥有竖直轴对称但非中心对称。',.97,[]),
9:('D','六图均含两个五边形，且每图直角总数均为4。①④⑥的两个五边形各有2个直角；②③⑤为一个1直角、另一个3直角。不能只数每幅总直角。',.93,['斜放的直角需逐角核对；同样用纯图像轮廓测角辅助，未读作者模型。']),
10:('B','两条虚线折线彼此只有一个相交点。①④⑤的交点在实线封闭图形外；②③⑥在内。实线四边形和虚线数量相同，分类依据是交点参照关系。',.98,[]),
}
reviews=[]
for card in cards:
 n=card['n'];a,rule,confidence,ambiguities=answers[n]
 actual=sha256(Path(card['image']).read_bytes()).hexdigest();assert actual==card['image_sha256']
 reviews.append(dict(n=n,answer=a,natural_rule=rule,confidence=confidence,ambiguities=ambiguities,
                     image_sha256=actual,actual_image_viewed=True))
report=dict(method='代理交叉独立求解，非教师盲审；仅读blind_cards_a及题图，未读A代码/答案/解析/模型。',
            all_ten_images_actually_viewed=True,current_revised_2_4_9_reviewed=True,
            external_assistance='Q4/Q9只对题图黑像素轮廓做测角辅助；未读取几何模型。',
            reviews=reviews,unresolved_same_natural_rule_alternative_answers=[])
(ROOT/'blind_review_a_by_b.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
card=next(c for c in json.loads((ROOT/'blind_cards_c.json').read_text(encoding='utf-8'))['cards'] if c['n']==30)
assert sha256(Path(card['image']).read_bytes()).hexdigest()==card['image_sha256']
review=dict(method='代理独立求解；仅读当前无提示C30卡和题图，未读C源代码、答案/解析或其他代理反馈。',
            n=30,answer='A',natural_rule='每幅由4个共边的小四边形组成。②④⑥呈T形连接，存在一个小面与其余3个小面均共边；①③⑤呈链状连接，每个小面至多与2个小面共边。',
            confidence=.98,ambiguities=['斜投影使小面看起来不是正方形，但上述共边连接关系与具体角度无关，不需要额外几何提示。'],
            alternative_equal_natural_partitions=[],actual_image_viewed=True,image_sha256=card['image_sha256'])
(ROOT/'blind_review_c30_by_b.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print('saved A10 and C30 independent reviews')
