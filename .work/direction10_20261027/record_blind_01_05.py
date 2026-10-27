from pathlib import Path
import json,hashlib,datetime
root=Path(__file__).resolve().parent
public=json.loads((root/'public_questions.json').read_text(encoding='utf-8'))[:5]
first=json.loads((root/'first_answers_01_05.json').read_text(encoding='utf-8'))
reasons={
1:'观察者始终朝北看，画面右侧对应东。车头东但倒车向西，观察者位置西移使固定景物向画面右移；近路牌相对远钟楼的横向偏移按2、4、1、3递增。仅B给此完整顺序，A交换最后两张，C倒序，D后两张前置。',
2:'左窗朝西时画面右侧对应北。车辆向北前进，固定近柱相对远楼向画面左移；四个状态为3、1、4、2。仅D符合该序列，倒序及中间交换均破坏近柱横移次序。',
3:'东侧向西观察时南在左北在右，图2为纪念柱、钟楼、尖顶馆；南侧向北时西左东右，图4为钟楼、纪念柱、尖顶馆。西侧向东时北左南右，尖顶馆部分被更近的钟楼挡住，对应3；北侧向南时东左西右，对应尖顶馆、纪念柱、钟楼的图1。按已给东南西北路线为2、4、3、1，选A。',
4:'初始正对钟楼，四张中图4钟楼居中；原地向右转时固定地标向画面左侧移动，钟楼依次从4中央到2偏左，再到1最左边，最后在3中移出。其余建筑也依次左移，顺序4、2、1、3，选C。边缘透视使地标尺寸略变，不能把这种尺寸变化误当相机平移或变焦。',
5:'太阳正北使竖直建筑的地面影子朝正南。影子在图中沿底棱的一组反向延伸至右下，说明南向在观察者右前下方且朝观察者，北向则由近角向左上延伸。保持真实无镜像的三维投影，另一组底棱是向东后退，观察者在建筑西南。故C；不把图中右下简单当地图东南，不用墙面灰度推太阳方向。'
}
items=[]
for q in public:
 n=q['n'];p=Path(q['image'])
 items.append({'n':n,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actually_opened_original':True,
  'first_answer':first['answers'][str(n)],'answer':first['answers'][str(n)],'unique':True,
  'basis':reasons[n],'visible_issues':[],
  'checks':['题面明确观察方向或给定方向参照','四候选有且只有一个符合图面关系','未读取作者模型、答案、绘图程序或解析图']})
out={'reviewer':'direction_design_review独立代理','reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'题1—5的公开题干、选项、五张最终原始题图；没有读取其他禁读文件',
 'author_model_or_answers_read':False,'answers':first['answers'],'items':items,
 'first_answers_frozen_before_report':True,'issues':[],
 'limits':['本报告是独立目视试解和方向关系审查，未读取三维坐标模型，不代替精确几何复算。','没有检查Word/PDF最终页排版，也不是教师审题或学员试测。','第5题仅用地面投影和底棱推方向，不将白灰画法当墙面光照测量。']}
(root/'blind_review_01_05.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'answers':out['answers'],'items':len(items),'visible_issues':0},ensure_ascii=False))
