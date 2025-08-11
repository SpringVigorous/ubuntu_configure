class ProjectInfo:
    """Represents information about a project including its name, maximum investment limit, and remaining days."""
    
    def __init__(self, name: str, max_limit: float, remaining_days: int):
        self.name = name  # Name of the project
        self.max_limit = max_limit  # Maximum investment allowed for the project
        self.remaining_days = remaining_days  # Remaining days for the project


#信用卡刷卡分配
def max_profit_allocation(total_amount: float, projects: list[ProjectInfo]):
    """
    Calculate the optimal investment allocation across projects to maximize total profit.
    
    Args:
        total_amount: Total available funds to invest
        projects: List of ProjectInfo objects representing available projects
        
    Returns:
        A tuple containing:
        - Dictionary of project names and their allocated investments
        - Maximum total profit achievable
    """
    # Sort projects by remaining days in descending order (higher days first)
    sorted_projects = sorted(projects, key=lambda x: -x.remaining_days)
    allocation = {}  # To store investment for each project by name
    remaining_funds = total_amount
    
    for project in sorted_projects:
        if remaining_funds <= 0:
            allocation[project.name] = 0.0
            continue
            
        # Invest the minimum of the project's max limit and remaining funds
        investment = min(project.max_limit, remaining_funds)
        allocation[project.name] = investment
        remaining_funds -= investment
    
    # Calculate total profit
    total_profit = sum(allocation[project.name] * project.remaining_days 
                      for project in projects)
    
    return allocation, total_profit


# Test the implementation
if __name__ == "__main__":
    # Create project instances
    project_a = ProjectInfo("A", 50, 28)
    project_b = ProjectInfo("B", 30, 48)
    project_c = ProjectInfo("C", 40, 51)
    
    total_funds = 100.0
    projects_list = [project_a, project_b, project_c]
    
    # Calculate optimal allocation
    investment_allocation, max_profit = max_profit_allocation(total_funds, projects_list)
    
    # Display results
    print("Optimal Investment Allocation:")
    for project_name, amount in investment_allocation.items():
        print(f"{project_name}: {amount}")
    
    print(f"\nMaximum Total Profit: {max_profit}")
