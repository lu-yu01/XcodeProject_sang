"""Square Q9-12 without stretching or changing original figure content."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from hashlib import sha256
from datetime import datetime
import json
from PIL import Image, ImageChops
from lxml import etree
import graphics_a
import drawkit as k

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
BASELINES=json.loads((ROOT.parent/'baselines.json').read_text(encoding='utf-8-sig'))
BASE=next(b for b in BASELINES if b['key']=='doc55')
SOURCE=Path(BASE['before']); OUTPUT=Path(BASE['output'])
OLD_ASSETS=Path(BASE['old_workdir'])/'assets'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
QUESTIONS=[9,10,11,12]
sha=lambda b:sha256(b).hexdigest()

def bounds_for_content(im,box):
    roi=im.crop(box)
    return ImageChops.difference(roi,Image.new('RGB',roi.size,'white')).getbbox()

def main():
    assert sha(SOURCE.read_bytes())==BASE['before_sha256']
    before_source=SOURCE.read_bytes()
    assert sha(OUTPUT.read_bytes())==BASE['before_sha256'],'Output changed since baseline; do not overwrite'
    with ZipFile(SOURCE) as z:
        original_xml=z.read('word/document.xml')
        doc=etree.fromstring(original_xml)
        rel=etree.fromstring(z.read('word/_rels/document.xml.rels'))
        rels={r.get('Id'):'word/'+r.get('Target') for r in rel if r.get('Type','').endswith('/image')}
        source_hashes={sha((OLD_ASSETS/f'q{n:02}.png').read_bytes()):n for n in range(1,31)}
        mapping={}
        for name in z.namelist():
            if name.startswith('word/media/'):
                n=source_hashes[sha(z.read(name))]
                mapping[n]=name
        assert len(mapping)==30
        replacements={}; details=[]
        for n in QUESTIONS:
            getattr(graphics_a,f'draw{n}')()
            layout=k.LAYOUTS[n]
            assert layout['outer_box']==[480,40,1320,880]
            assert layout['cell_sizes']==[[280,280]]*9
            media=mapping[n]
            old=Image.open(BytesIO(z.read(media))).convert('RGB')
            new=Image.open(ROOT/'assets'/f'q{n:02}.png').convert('RGB')
            assert old.size==new.size==(1800,1170)
            # The full canvas outside the former matrix is exactly unchanged.
            for box in [(0,0,1800,40),(0,881,1800,1170),(0,40,450,881),(1351,40,1800,881)]:
                assert ImageChops.difference(old.crop(box),new.crop(box)).getbbox() is None
            # Includes option shapes, frame, A-D letters, whitespace and all pixels.
            assert ImageChops.difference(old.crop((0,900,1800,1170)),new.crop((0,900,1800,1170))).getbbox() is None
            content_checks=[]
            for i,(new_x,new_y) in enumerate(layout['stem_centers']):
                row,col=divmod(i,3)
                old_x=600+300*col;old_y=180+280*row
                old_box=(old_x-125,old_y-125,old_x+125,old_y+125)
                new_box=tuple(map(int,(new_x-125,new_y-125,new_x+125,new_y+125)))
                a=old.crop(old_box);b=new.crop(new_box)
                assert ImageChops.difference(a,b).getbbox() is None,(n,i,'stem content pixels differ')
                # Check the complete interior beyond framing also stays in ROI.
                interior=(450+300*col+6,40+280*row+6,450+300*(col+1)-6,40+280*(row+1)-6)
                local_bbox=bounds_for_content(old,interior)
                assert local_bbox is not None
                actual_box=[local_bbox[0]+interior[0],local_bbox[1]+interior[1],local_bbox[2]+interior[0],local_bbox[3]+interior[1]]
                assert old_box[0]<=actual_box[0] and old_box[1]<=actual_box[1] and actual_box[2]<=old_box[2] and actual_box[3]<=old_box[3]
                actual_new=[actual_box[0]+new_x-old_x,actual_box[1],actual_box[2]+new_x-old_x,actual_box[3]]
                cell=[480+280*col,40+280*row,480+280*(col+1),40+280*(row+1)]
                gaps=[actual_new[0]-cell[0],actual_new[1]-cell[1],cell[2]-actual_new[2],cell[3]-actual_new[3]]
                assert min(gaps)>15,(n,i,'content too close to grid')
                content_checks.append({'cell':i+1,'old_center':[old_x,old_y],'new_center':[new_x,new_y],
                    'translation':[new_x-old_x,new_y-old_y],'old_roi':old_box,'new_roi':new_box,
                    'pixel_identical_after_translation':True,'rgb_sha256':sha(a.tobytes()),
                    'actual_artwork_bbox_old':actual_box,'actual_artwork_bbox_new':actual_new,
                    'artwork_clearance_px_ltrb':gaps})
            rid=next(r for r,v in rels.items() if v==media)
            blips=doc.xpath('.//a:blip[@r:embed=$rid]',namespaces=NS,rid=rid)
            assert len(blips)==1
            inline=blips[0]
            while inline.tag!='{'+NS['wp']+'}inline':inline=inline.getparent()
            wp=inline.find('wp:extent',namespaces=NS)
            ext=inline.find('.//pic:spPr/a:xfrm/a:ext',namespaces=NS)
            cx,cy=int(wp.get('cx')),int(wp.get('cy'))
            assert dict(wp.attrib)==dict(ext.attrib)
            # Integer EMU serialization may differ by < 0.5 EMU from exact ratio.
            assert abs(cy-cx*new.height/new.width)<=0.5
            replacements[media]=(ROOT/'assets'/f'q{n:02}.png').read_bytes()
            details.append({'question':n,'media':media,'relationship_id':rid,
                'old_png_size':old.size,'new_png_size':new.size,
                'old_outer_box':[450,40,1350,880],'new_outer_box':layout['outer_box'],
                'old_outer_dimensions':[900,840],'new_outer_dimensions':[840,840],
                'old_cell_sizes':[[300,280]]*9,'new_cell_sizes':layout['cell_sizes'],
                'old_stem_centers':[[600+300*c,180+280*r] for r in range(3) for c in range(3)],
                'new_stem_centers':layout['stem_centers'],'option_centers_unchanged':layout['option_centers'],
                'options_full_roi':[0,900,1800,1170],'options_pixel_identical':True,
                'source_png_sha256':sha(z.read(media)),'new_png_sha256':sha(replacements[media]),
                'content_roi_checks':content_checks,'wp_extent_unchanged':dict(wp.attrib),
                'picture_extent_unchanged':dict(ext.attrib),'ratio_rounding_error_emu':cy-cx*new.height/new.width,
                'word_scaling_proportional':True})
        temp=ROOT/'revised.docx'
        with ZipFile(temp,'w') as out:
            for info in z.infolist():out.writestr(info,replacements.get(info.filename,z.read(info.filename)))
    with ZipFile(SOURCE) as a,ZipFile(temp) as b:
        differences=[name for name in a.namelist() if a.read(name)!=b.read(name)]
        assert set(differences)==set(replacements)
        assert a.read('word/document.xml')==b.read('word/document.xml')
        assert a.read('word/numbering.xml')==b.read('word/numbering.xml')
    # The baseline and all previous-run assets remain untouched.
    assert SOURCE.read_bytes()==before_source
    try:
        temp.replace(OUTPUT)
    except PermissionError:
        raise SystemExit('OUTPUT_LOCKED: revised.docx retained; report to parent before retry')
    report={'status':'geometry_content_and_ooxml_checks_passed_waiting_render',
        'time':datetime.now().astimezone().isoformat(),'source_word':str(SOURCE),'output_word':str(OUTPUT),
        'source_sha256':BASE['before_sha256'],'output_sha256':sha(OUTPUT.read_bytes()),
        'changed_questions':QUESTIONS,'all_true_ninegrid_questions':[9,10,11,12],
        'question_count':55,'embedded_image_count':30,
        'changed_zip_members':differences,'document_xml_byte_identical':True,
        'numbering_xml_byte_identical':True,'other_26_embedded_images_byte_identical':True,
        'all_other_zip_members_byte_identical':True,
        'all_36_stem_content_rois_pixel_identical_after_translation':True,
        'all_option_pixels_identical':True,'all_word_image_extents_unchanged':True,
        'layout_strategy':'Narrow each ninegrid to a centered 840x840 square; use 280x280 cells. Translate columns +20/0/-20 px; no scaling, rotation, redrawing of artwork or option changes.',
        'per_question':details}
    (ROOT/'change_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'figure_layout.json').write_text(json.dumps(k.LAYOUTS,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output_word':str(OUTPUT),'output_sha256':report['output_sha256'],
        'changed_questions':QUESTIONS,'geometry':'840x840 / 280x280','content_roi_checks':36},ensure_ascii=False))

if __name__=='__main__':main()
