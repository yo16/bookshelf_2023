from flask_login import current_user

from models import get_db, DbOrganization


def get_org_mem():
    """組織とメンバー情報を取得

    Returns:
        dict: {organization:DbOrganization, member:DbMember}
    """
    org = None
    with get_db() as db:
        org = DbOrganization.get(db, current_user.org_id)

    return {
        "organization": org,
        "member": current_user
    }
