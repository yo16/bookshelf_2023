from flask import render_template, redirect, url_for

from models import get_db, DbOrganization, DbMember


def main(app):
    debug = app.config["DEBUG"]
    if not debug:
        return redirect(url_for("main"))
    
    from sqlalchemy import select
    db = next(get_db())
    #result = db.execute(select(DbOrganization)).scalars().all()
    result = db.execute(select(DbMember)).scalars().all()
    #count = result.count()
    #text = f"DbOrganization count:{count}"
    print(result)
    len_result = len(result)
    text = f"count:{len_result}"
    for c in result:
        print('----')
        print(c.org_id)
    
    # join
    print('join test')
    result = db.execute(
        select(DbOrganization.org_id, DbOrganization.org_name, DbMember.member_id, DbMember.member_name)
        .join(DbMember, DbOrganization.org_id == DbMember.org_id)
    #).scalars().all()
    ).all()
    print('len---')
    print(len(result))
    print(result)
    for row in result:
        print(row)
        print(type(row))
        print('++++')
        print(f"org_id:{row.org_id}, org_name:{row.org_name}, mem_id:{row.member_id}, mem_nm:{row.member_name}")

    return render_template("test.html")

