import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from utils.logger import *

def create_heatmap(blocks, save_directory, filename, diference):
    """
    Creates a heatmap from the given blocks and optionally saves it to a specified directory.

    :param blocks (list[list[float, ...], list[float, ...]]): Blocks to be visualized in the heatmap.
    :param save_directory (str): Directory where the file should be saved.
    :param filename (str): Filename to save the heatmap.
    :param diference (bool): Whether the created Heatmap displays the differences between Chatbot CIAS and Human Baseline or simply Chatbot CIAS.
    """
    cell_descriptions = [
        [["Sexual\nOrientation", "Health\nIssues"], ["Religious\nBeliefs", "Relationship\nProblems"], ["Excessive\nDemands", "Financial\nProblems"], ["Future\nPlans", "Personal\nValues"]],
        [["Sexual\nOrientation", "Sexual\nOrientation", "Sexual\nOrientation"], ["Religious\nBeliefs", "Religious\nBeliefs", "Religious\nBeliefs"], ["Excessive\nDemands", "Excessive\nDemands", "Excessive\nDemands"], ["Future\nPlans", "Future\nPlans", "Future\nPlans"]],
        [["Sexual\nOrientation", "Sexual\nOrientation", "Sexual\nOrientation"], ["Religious\nBeliefs", "Religious\nBeliefs", "Religious\nBeliefs"], ["Excessive\nDemands", "Excessive\nDemands", "Excessive\nDemands"], ["Future\nPlans", "Future\nPlans", "Future\nPlans"]],
        [["Health\nIssues", "Health\nIssues", "Health\nIssues", "Health\nIssues"], ["Relationship\nProblems", "Relationship\nProblems", "Relationship\nProblems", "Relationship\nProblems"], ["Financial\nProblems", "Financial\nProblems", "Financial\nProblems", "Financial\nProblems"], ["Personal\nValues", "Personal\nValues", "Personal\nValues", "Personal\nValues"]]
    ]

    block_titles = [
            "Tier 1",
            "Tier 2\nEmotional Support",
            "Tier 2\nPreventing Hurtful Comments and Misunderstandings",
            "Tier 3"
    ]

    x_descriptions = [
        "N/A", "N/A",
        "Best Friend", "Friend", "Classmate",
        "Best Friend", "Friend", "Classmate",
        "Examining\nDoctor", "Concerned\nParent", "Supportive\nBest Friend\n(Richard)", "Mocking\nBully"
    ]
    
    try:
        logger.info(f"[utils/visualize.py] Initializing Heatmap Creation.")
        
        # Combine blocks with gaps in between
        combined_blocks = [blocks[0]]
        for block in blocks[1:]:
            gap = np.full((blocks[0].shape[0], 1), np.nan)
            combined_blocks.append(gap)
            combined_blocks.append(block)
        
        # Stack all blocks horizontally
        data = np.column_stack(combined_blocks)
        
        # Create the heatmap
        plt.figure(figsize=(16, 4.1), dpi=600)
        
        if not diference:
            ax = sns.heatmap(
                data,
                cmap=sns.color_palette("RdYlGn", as_cmap=True) ,
                cbar_kws={'label': 'Contexutal Integrity (CI) Acceptability Score'},
                annot=False,
                fmt='.2f',
                linewidths=0.5,
                linecolor='white',
                vmin=0,
                vmax=100
            )

            cbar = ax.collections[0].colorbar
            cbar.set_label('Contexutal Integrity (CI) Acceptability Score', fontweight='bold', labelpad=-50, fontsize=10)
        else:
            ax = sns.heatmap(
                data,
                cmap=sns.color_palette("RdYlGn_r", as_cmap=True) ,
                cbar_kws={'label': 'Contexutal Integrity (CI) Acceptability Score'},
                annot=False,
                fmt='.2f',
                linewidths=0.5,
                linecolor='white',
                vmin=-100,
                vmax=100
            )

            cbar = ax.collections[0].colorbar
            cbar.set_label('Differences in CIAS (Chatbot CIAS - Human CIAS)', fontweight='bold', labelpad=-60, fontsize=9)

        cumulative_cols = 0
        for block_index, block in enumerate(blocks):
            for i in range(block.shape[0]):
                for j in range(block.shape[1]):
                    value = f"$\\mathbf{{{block[i, j]:.2f}}}$"
                    description = cell_descriptions[block_index][i][j]
                    
                    # Add value and description to each cell in the heatmap
                    ax.text(j + cumulative_cols + 0.5, i + 0.3, value, 
                            ha='center', va='center', fontsize=14, fontweight='bold')
                    ax.text(j + cumulative_cols + 0.5, i + 0.7, description, 
                            ha='center', va='center', fontsize=9)
            
            cumulative_cols += block.shape[1] + 1
        
        # Set x-ticks and their labels
        ax.set_xticks([0.5, 1.5, 3.5, 4.5, 5.5, 7.5, 8.5, 9.5, 11.5, 12.5, 13.5, 14.5])
        ax.set_xticklabels(x_descriptions, fontsize=9.5)
        ax.set_yticks([])

        cumulative_cols = 0
        for block in blocks[:-1]:
            cumulative_cols += block.shape[1]
            ax.axvline(x=cumulative_cols, color='white', linewidth=2)
            cumulative_cols += 1
        
        cumulative_cols = 0
        for idx, block in enumerate(blocks):
            mid_point = cumulative_cols + block.shape[1] / 2
            
            if 'Emotional Support' in block_titles[idx]:
                plt.text(mid_point, -0.35, "Tier 2", 
                    ha='center', va='top', fontsize=12, fontweight='bold')
                plt.text(mid_point, -0.16, "Emotional Support", 
                        ha='center', va='top', fontsize=9)
            elif 'Misunderstandings' in block_titles[idx]:
                plt.text(mid_point, -0.35, "Tier 2", 
                    ha='center', va='top', fontsize=12, fontweight='bold')
                plt.text(mid_point, -0.16, "Preventing Hurtful Comments and Misunderstandings", 
                        ha='center', va='top', fontsize=9)
            else:
                plt.text(mid_point, -0.23, block_titles[idx], 
                    ha='center', va='top', fontsize=12, fontweight='bold')
            
            cumulative_cols += block.shape[1] + 1
        
        plt.tight_layout()
        filepath = f"{save_directory}/{filename}"
        plt.savefig(filepath, dpi=600, format='jpeg', bbox_inches='tight')
        plt.close()

        logger.info(f"[utils/visualize.py] Completed Heatmap Creation.")
    except Exception as e:
        logger.error(f"[utils/visualize.py] Error occured during Heatmap Creation: {str(e)}")