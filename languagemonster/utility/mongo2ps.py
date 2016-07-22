from core import models_mongo as models #mongo
from core import models as models2 #postgre

DB = 'default'

def cp_Language():
    models2.Language.objects.using(DB).all().delete()
    items = models.Language.objects.all()

    for item in items:
        new = models2.Language(
            english_name=item.english_name,
            original_name=item.original_name,
            acronym=item.acronym,
            image_filename=item.image_filename,
            flag_filename=item.flag_filename,
            linked=item.linked,
        )
        new.save(using=DB)

def cp_LanguagePair():
    models2.LanguagePair.objects.using(DB).all().delete()
    items = models.LanguagePair.objects.all()

    for item in items:
        bl = models2.Language.objects.using(DB).get(acronym=item.base_language.acronym)
        tl = models2.Language.objects.using(DB).get(acronym=item.target_language.acronym)
        new = models2.LanguagePair(
            visible=item.visible,
            learners=item.learners,
            base_language=bl,
            target_language=tl,
        )
        new.save(using=DB)

def cp_BaseLanguage():
    models2.BaseLanguage.objects.using(DB).all().delete()
    items = models.BaseLanguage.objects.all()

    for item in items:
        l = models2.Language.objects.using(DB).get(acronym=item.language.acronym)

        new = models2.BaseLanguage(
            flag_filename=item.flag_filename,
            original_name=item.original_name,
            country=item.country,
            visible=item.visible,

            language=l,
        )
        new.save(using=DB)

def find_pair(pair):
    bl_a = pair.base_language.acronym
    tl_a = pair.target_language.acronym

    bl = models2.Language.objects.using(DB).get(acronym=bl_a)
    tl = models2.Language.objects.using(DB).get(acronym=tl_a)

    return models2.LanguagePair.objects.using(DB).get(
        base_language=bl,
        target_language=tl,
    )

def cp_DataSet():
    models2.DataSet.objects.using(DB).all().delete()
    items = models.DataSet.objects.all()

    for item in items:
        new = models2.DataSet(
            name_en=item.name_en,
            name_base=item.name_base,
            name_target=item.name_target,
            slug=item.slug,
            icon=item.icon,
            visible=item.visible,
            from_exported_file=item.from_exported_file,
            word_count=item.word_count,
            pos=item.pos,
            learners=item.learners,
            simple_dataset=item.simple_dataset,
            reversed_set=item.reversed_set,

            pair=find_pair(item.pair),
        )
        new.save(using=DB)

def find_dataset(dataset):
    i = models2.DataSet.objects.using(DB).get(
        name_en=dataset.name_en,
        name_base=dataset.name_base,
        name_target=dataset.name_target,
        slug=dataset.slug,
        icon=dataset.icon,
        visible=dataset.visible,
        from_exported_file=dataset.from_exported_file,
        word_count=dataset.word_count,
        pos=dataset.pos,
    )

    return i

def cp_WordPair():
    models2.WordPair.objects.using(DB).all().delete()
    items = models.WordPair.objects.all()

    for item in items:
        new = models2.WordPair(
            base=item.base,
            target=item.target,
            english=item.english,
            comments=item.comments,
            pos=item.pos,
            base_en=item.base_en,
            target_en=item.target_en,
            english_invalid=item.english_invalid,
            from_english=item.from_english,
            verified=item.verified,
            index=item.index,
            pop=item.pop,

            data_set=None,
        )
        new.save(using=DB)

def find_wordpair(wp):
    print wp.__dict__
    i = models2.WordPair.objects.using(DB).filter(
        base=wp.base,
        target=wp.target,
        english=wp.english,
        comments=wp.comments,
        pos=wp.pos,
        base_en=wp.base_en,
        target_en=wp.target_en,
        pop=wp.pop,
        index=wp.index,
        verified=wp.verified,
        from_english=wp.from_english,
        english_invalid=wp.english_invalid,
    ).first()

    print i
    print i.__dict__

    # if not isinstance(i, models2.WordPair):
    #     print i
    #     for j in i:
    #         print j.__dict__

    return i

def cp_SimpleDatasets():
    models2.SimpleDataset.objects.using(DB).all().delete()
    items = models.SimpleDataset.objects.all()

    for item in items:
        new = models2.SimpleDataset(
            name=item.name,
            data=item.data,
        )
        new.save(using=DB)

def cp_DS2WP():
    models2.DS2WP.objects.using(DB).all().delete()
    items = models.DS2WP.objects.all()

    for item in items:
        if isinstance(item.ds, models.DataSet) and isinstance(item.wp, models.WordPair):
            new = models2.DS2WP(
                ds=find_dataset(item.ds),
                wp=find_wordpair(item.wp),
            )
            new.save(using=DB)

def cp_All():
    cp_Language()
    cp_LanguagePair()
    cp_BaseLanguage()
    cp_DataSet()
    cp_WordPair()
    cp_SimpleDatasets()
    cp_DS2WP()