from flask_login import current_user

from models import DbOrganization


def get_org_mem():
    """組織とメンバー情報を取得

    Returns:
        dict: {organization:DbOrganization, member:DbMember}
    """
    return {
        "organization": DbOrganization.get(current_user.org_id),
        "member": current_user
    }
